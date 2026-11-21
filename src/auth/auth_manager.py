"""
Enterprise Multi-Tenant Authentication & Role-Based Access Control (RBAC).
Provides:
- SQLite persistence for users and document permissions
- Salted password hashing (PBKDF2-HMAC-SHA256)
- Signed JWT token generation and verification
- Document authorization rules: Admin (All), Auditor (Contracts & Invoices), User (Owned + Public)
"""

import os
import sqlite3
import hashlib
import secrets
import jwt
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

JWT_SECRET = "doculens-enterprise-production-rag-auth-secret-key-32bytes"
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data")
DB_PATH = os.path.join(DATA_DIR, "enterprise_auth.db")

class AuthManager:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()
        self._seed_default_users_and_permissions()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # 1. Users Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user', -- 'admin', 'auditor', 'user'
                department TEXT DEFAULT 'general',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

            # 2. Document Access Control Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS document_permissions (
                id TEXT PRIMARY KEY,
                document_filename TEXT UNIQUE NOT NULL,
                owner_user_id TEXT NOT NULL,
                is_public INTEGER DEFAULT 0, -- 1 = public, 0 = restricted
                allowed_roles TEXT DEFAULT 'admin', -- comma-separated: 'admin,auditor,user'
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)
            conn.commit()

    @staticmethod
    def _hash_password(password: str, salt: str) -> str:
        return hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        ).hex()

    def _seed_default_users_and_permissions(self):
        default_users = [
            ("usr-admin", "admin", "System Administrator", "admin@doculens.corp", "admin123", "admin", "IT & Governance"),
            ("usr-auditor", "auditor", "Legal & Financial Auditor", "auditor@doculens.corp", "auditor123", "auditor", "Finance"),
            ("usr-sheik", "sheik", "Sheik Mohammed", "sheik@doculens.corp", "sheik123", "user", "Engineering")
        ]

        with self._get_connection() as conn:
            cursor = conn.cursor()
            for uid, uname, fname, email, pwd, role, dept in default_users:
                cursor.execute("SELECT id FROM users WHERE username = ?", (uname,))
                if not cursor.fetchone():
                    salt = secrets.token_hex(16)
                    pwd_hash = self._hash_password(pwd, salt)
                    cursor.execute("""
                        INSERT INTO users (id, username, full_name, email, password_hash, salt, role, department)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (uid, uname, fname, email, pwd_hash, salt, role, dept))

            # Seed permissions for sample documents
            doc_rules = [
                ("Sheik_Mohammed_Resume.pdf", "usr-sheik", 0, "admin"),
                ("MSA_Acme_Cyberdyne_2024.pdf", "usr-auditor", 0, "admin,auditor"),
                ("SOW_Cloud_Infrastructure.pdf", "usr-auditor", 0, "admin,auditor"),
                ("INV_2024_081_Compliant.pdf", "usr-auditor", 0, "admin,auditor"),
                ("INV_2024_099_Disputed.pdf", "usr-auditor", 0, "admin,auditor"),
            ]

            for doc_name, owner_id, is_pub, roles in doc_rules:
                cursor.execute("SELECT id FROM document_permissions WHERE document_filename = ?", (doc_name,))
                existing_perm = cursor.fetchone()
                if not existing_perm:
                    pid = f"perm-{secrets.token_hex(8)}"
                    cursor.execute("""
                        INSERT INTO document_permissions (id, document_filename, owner_user_id, is_public, allowed_roles)
                        VALUES (?, ?, ?, ?, ?)
                    """, (pid, doc_name, owner_id, is_pub, roles))
                else:
                    cursor.execute("""
                        UPDATE document_permissions
                        SET owner_user_id = ?, is_public = ?, allowed_roles = ?
                        WHERE document_filename = ?
                    """, (owner_id, is_pub, roles, doc_name))

            conn.commit()

    def register_user(self, username: str, full_name: str, email: str, password: str, role: str = "user", department: str = "general") -> Dict[str, Any]:
        username = username.strip().lower()
        email = email.strip().lower()

        # Security Enforcement: All public sign-ups are strictly constrained to 'user' role
        role = "user"

        if username == "admin":
            raise ValueError("The 'admin' username is reserved and cannot be registered.")

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE username = ? OR email = ?", (username, email))
            if cursor.fetchone():
                raise ValueError("Username or email already registered.")

            user_id = f"usr-{secrets.token_hex(8)}"
            salt = secrets.token_hex(16)
            pwd_hash = self._hash_password(password, salt)

            cursor.execute("""
                INSERT INTO users (id, username, full_name, email, password_hash, salt, role, department)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, username, full_name, email, pwd_hash, salt, role, department))
            conn.commit()

            return {
                "id": user_id,
                "username": username,
                "full_name": full_name,
                "email": email,
                "role": role,
                "department": department
            }

    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        username = username.strip().lower()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            if not row:
                return None

            expected_hash = self._hash_password(password, row["salt"])
            if secrets.compare_digest(expected_hash, row["password_hash"]):
                return {
                    "id": row["id"],
                    "username": row["username"],
                    "full_name": row["full_name"],
                    "email": row["email"],
                    "role": row["role"],
                    "department": row["department"]
                }
        return None

    def create_access_token(self, user_info: Dict[str, Any]) -> str:
        payload = {
            "sub": user_info["id"],
            "username": user_info["username"],
            "role": user_info["role"],
            "full_name": user_info["full_name"],
            "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
        }
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return payload
        except Exception:
            return None

    def get_user_permitted_documents(self, user_id: str, role: str) -> List[str]:
        """
        Calculates the exact list of document filenames this user has clearance to query.
        - Admin: full access to all documents.
        - Auditor: financial/legal contracts + owned + public.
        - User: only their owned documents + public.
        """
        if role == "admin":
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT document_filename FROM document_permissions")
                rows = cursor.fetchall()
                return [r["document_filename"] for r in rows]

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT document_filename, owner_user_id, is_public, allowed_roles
                FROM document_permissions
            """)
            rows = cursor.fetchall()
            permitted = []
            for r in rows:
                doc = r["document_filename"]
                owner = r["owner_user_id"]
                is_pub = bool(r["is_public"])
                roles_list = [x.strip() for x in r["allowed_roles"].split(",")]

                # Condition 1: User is owner
                if owner == user_id:
                    permitted.append(doc)
                # Condition 2: Document is public
                elif is_pub:
                    permitted.append(doc)
                # Condition 3: Role-based clearance (for auditors)
                # Note: regular 'user' role is strictly isolated to their own uploaded documents
                elif role != "user" and role in roles_list:
                    permitted.append(doc)

            return permitted

    def assign_document_permission(self, document_filename: str, owner_user_id: str, is_public: bool = False, allowed_roles: str = "admin"):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM document_permissions WHERE document_filename = ?", (document_filename,))
            existing = cursor.fetchone()
            if existing:
                cursor.execute("""
                    UPDATE document_permissions 
                    SET owner_user_id = ?, is_public = ?, allowed_roles = ?
                    WHERE document_filename = ?
                """, (owner_user_id, 1 if is_public else 0, allowed_roles, document_filename))
            else:
                pid = f"perm-{secrets.token_hex(8)}"
                cursor.execute("""
                    INSERT INTO document_permissions (id, document_filename, owner_user_id, is_public, allowed_roles)
                    VALUES (?, ?, ?, ?, ?)
                """, (pid, document_filename, owner_user_id, 1 if is_public else 0, allowed_roles))
            conn.commit()

    def list_users(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, full_name, email, role, department, created_at FROM users")
            return [dict(r) for r in cursor.fetchall()]
