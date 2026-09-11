import pytest
from utils.auth import hash_password, verify_password, generar_session_token
from database.db import SessionLocal, init_db
from database.models import Usuario
from routers.auth import api_register, api_login
from database.schemas import UsuarioRegistroRequest, UsuarioLoginRequest
from fastapi import Response, HTTPException


class TestAuthUtils:
    def test_hash_and_verify_password(self):
        pwd = "MiContraseñaSecreta123!"
        h, salt = hash_password(pwd)
        assert len(h) == 64
        assert len(salt) > 0
        assert verify_password(pwd, h, salt) is True
        assert verify_password("PasswordErronea", h, salt) is False

    def test_different_salt_produces_different_hashes(self):
        pwd = "Password123"
        h1, s1 = hash_password(pwd)
        h2, s2 = hash_password(pwd)
        assert s1 != s2
        assert h1 != h2
        assert verify_password(pwd, h1, s1) is True
        assert verify_password(pwd, h2, s2) is True


class TestAuthFlow:
    @pytest.fixture(autouse=True)
    def setup_db(self):
        init_db()
        self.db = SessionLocal()
        # Limpiar usuarios de prueba si existen
        self.db.query(Usuario).filter(Usuario.nombre_usuario.in_(["auth_test_1", "auth_test_2"])).delete(synchronize_session=False)
        self.db.commit()
        yield
        self.db.query(Usuario).filter(Usuario.nombre_usuario.in_(["auth_test_1", "auth_test_2"])).delete(synchronize_session=False)
        self.db.commit()
        self.db.close()

    def test_registro_exitoso(self):
        req = UsuarioRegistroRequest(
            nombre_usuario="auth_test_1",
            email="auth_test_1@example.com",
            password="PasswordSegura123"
        )
        user = api_register(req, self.db)
        assert user.id_usuario is not None
        assert user.nombre_usuario == "auth_test_1"
        assert user.email == "auth_test_1@example.com"
        assert user.password_hash is not None
        assert verify_password("PasswordSegura123", user.password_hash, user.salt) is True

    def test_login_con_email_y_con_usuario(self):
        # 1. Registrar
        req_reg = UsuarioRegistroRequest(
            nombre_usuario="auth_test_2",
            email="auth_test_2@example.com",
            password="PasswordTest456"
        )
        api_register(req_reg, self.db)

        # 2. Login con Email
        resp = Response()
        login_mail = api_login(UsuarioLoginRequest(email_o_usuario="auth_test_2@example.com", password="PasswordTest456"), resp, self.db)
        assert login_mail["status"] == "ok"
        assert login_mail["usuario"]["nombre_usuario"] == "auth_test_2"

        # 3. Login con Nombre de Usuario
        login_user = api_login(UsuarioLoginRequest(email_o_usuario="auth_test_2", password="PasswordTest456"), resp, self.db)
        assert login_user["status"] == "ok"

        # 4. Login con Contraseña Incorrecta
        with pytest.raises(HTTPException) as exc:
            api_login(UsuarioLoginRequest(email_o_usuario="auth_test_2", password="WrongPassword"), resp, self.db)
        assert exc.value.status_code == 401
