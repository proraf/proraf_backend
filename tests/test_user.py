import pytest
from fastapi import status


@pytest.fixture
def admin_headers(client, api_headers, db_session):
    """Headers com autenticação de administrador"""
    from proraf.models.user import User
    from proraf.security import get_password_hash
    
    # Cria usuário admin
    admin = User(
        nome="Admin User",
        email="admin@proraf.com",
        senha=get_password_hash("admin123"),
        tipo_pessoa="F",
        cpf="00000000000",
        tipo_perfil="admin"
    )
    db_session.add(admin)
    db_session.commit()
    
    # Faz login
    response = client.post(
        "/auth/login",
        data={
            "username": "admin@proraf.com",
            "password": "admin123"
        },
        headers=api_headers
    )
    
    token = response.json()["access_token"]
    
    return {
        **api_headers,
        "Authorization": f"Bearer {token}"
    }


def test_admin_create_user(client, admin_headers):
    """Testa criação de usuário por admin"""
    response = client.post(
        "/admin/users/",
        json={
            "nome": "Novo Usuário",
            "email": "novo@test.com",
            "senha": "senha123",
            "tipo_pessoa": "F",
            "cpf": "11111111111",
            "tipo_perfil": "user"
        },
        headers=admin_headers
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == "novo@test.com"
    assert data["tipo_perfil"] == "user"


def test_admin_create_admin_user(client, admin_headers):
    """Testa criação de usuário admin por admin"""
    response = client.post(
        "/admin/users/",
        json={
            "nome": "Novo Admin",
            "email": "newadmin@test.com",
            "senha": "senha123",
            "tipo_pessoa": "J",
            "cnpj": "12345678000190",
            "tipo_perfil": "admin"
        },
        headers=admin_headers
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["tipo_perfil"] == "admin"


def test_regular_user_cannot_create_user(client, auth_headers):
    """Testa que usuário comum não pode criar usuário"""
    response = client.post(
        "/admin/users/",
        json={
            "nome": "Novo Usuário",
            "email": "novo@test.com",
            "senha": "senha123",
            "tipo_pessoa": "F",
            "cpf": "11111111111"
        },
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_admin_list_all_users(client, admin_headers, db_session):
    """Testa listagem de todos usuários por admin"""
    from proraf.models.user import User
    from proraf.security import get_password_hash
    
    # Cria usuários de teste
    users = [
        User(nome="User 1", email="user1@test.com", senha=get_password_hash("pass"), tipo_pessoa="F", cpf="11111111111"),
        User(nome="User 2", email="user2@test.com", senha=get_password_hash("pass"), tipo_pessoa="J", cnpj="11111111000111"),
        User(nome="User 3", email="user3@test.com", senha=get_password_hash("pass"), tipo_pessoa="F", cpf="22222222222"),
    ]
    for u in users:
        db_session.add(u)
    db_session.commit()
    
    response = client.get("/admin/users/", headers=admin_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 4  # 3 criados + 1 admin da fixture


def test_admin_list_users_with_filters(client, admin_headers, db_session):
    """Testa filtros na listagem de usuários"""
    from proraf.models.user import User
    from proraf.security import get_password_hash
    
    users = [
        User(nome="Admin 2", email="admin2@test.com", senha=get_password_hash("pass"), tipo_pessoa="F", cpf="11111111111", tipo_perfil="admin"),
        User(nome="User PF", email="userpf@test.com", senha=get_password_hash("pass"), tipo_pessoa="F", cpf="22222222222", tipo_perfil="user"),
        User(nome="User PJ", email="userpj@test.com", senha=get_password_hash("pass"), tipo_pessoa="J", cnpj="11111111000111", tipo_perfil="user"),
    ]
    for u in users:
        db_session.add(u)
    db_session.commit()
    
    # Filtro por perfil
    response = client.get("/admin/users/?tipo_perfil=admin", headers=admin_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert all(u["tipo_perfil"] == "admin" for u in data)
    
    # Filtro por tipo pessoa
    response = client.get("/admin/users/?tipo_pessoa=J", headers=admin_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert all(u["tipo_pessoa"] == "J" for u in data)


def test_admin_get_user_by_id(client, admin_headers, db_session):
    """Testa busca de usuário por ID"""
    from proraf.models.user import User
    from proraf.security import get_password_hash
    
    user = User(
        nome="Test User",
        email="testuser@test.com",
        senha=get_password_hash("pass"),
        tipo_pessoa="F",
        cpf="12345678901"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    response = client.get(f"/admin/users/{user.id}", headers=admin_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == user.id
    assert data["email"] == "testuser@test.com"


def test_admin_get_user_by_email(client, admin_headers, db_session):
    """Testa busca de usuário por email"""
    from proraf.models.user import User
    from proraf.security import get_password_hash
    
    user = User(
        nome="Email User",
        email="emailuser@test.com",
        senha=get_password_hash("pass"),
        tipo_pessoa="F",
        cpf="12345678901"
    )
    db_session.add(user)
    db_session.commit()
    
    response = client.get("/admin/users/email/emailuser@test.com", headers=admin_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == "emailuser@test.com"


def test_admin_get_nonexistent_user(client, admin_headers):
    """Testa busca de usuário inexistente"""
    response = client.get("/admin/users/9999", headers=admin_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_admin_update_user(client, admin_headers, db_session):
    """Testa atualização de usuário por admin"""
    from proraf.models.user import User
    from proraf.security import get_password_hash
    
    user = User(
        nome="Old Name",
        email="oldname@test.com",
        senha=get_password_hash("pass"),
        tipo_pessoa="F",
        cpf="12345678901",
        telefone="51999999999"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    response = client.put(
        f"/admin/users/{user.id}",
        json={
            "nome": "New Name",
            "telefone": "51888888888"
        },
        headers=admin_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["nome"] == "New Name"
    assert data["telefone"] == "51888888888"


def test_admin_update_user_password(client, admin_headers, db_session, api_headers):
    """Testa atualização de senha por admin"""
    from proraf.models.user import User
    from proraf.security import get_password_hash
    
    user = User(
        nome="Password User",
        email="passuser@test.com",
        senha=get_password_hash("oldpass"),
        tipo_pessoa="F",
        cpf="12345678901"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    # Admin atualiza senha
    response = client.put(
        f"/admin/users/{user.id}",
        json={"senha": "newpass123"},
        headers=admin_headers
    )
    assert response.status_code == status.HTTP_200_OK
    
    # Testa login com nova senha
    response = client.post(
        "/auth/login",
        data={"username": "passuser@test.com", "password": "newpass123"},
        headers=api_headers
    )
    assert response.status_code == status.HTTP_200_OK


def test_admin_delete_user(client, admin_headers, db_session):
    """Testa deleção de usuário por admin"""
    from proraf.models.user import User
    from proraf.security import get_password_hash
    
    user = User(
        nome="Delete User",
        email="delete@test.com",
        senha=get_password_hash("pass"),
        tipo_pessoa="F",
        cpf="12345678901"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    user_id = user.id
    
    response = client.delete(f"/admin/users/{user_id}", headers=admin_headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verifica que foi deletado
    deleted = db_session.query(User).filter(User.id == user_id).first()
    assert deleted is None


def test_admin_cannot_delete_self(client, admin_headers, db_session):
    """Testa que admin não pode deletar a si mesmo"""
    from proraf.models.user import User
    
    # Busca o admin logado
    admin = db_session.query(User).filter(User.email == "admin@proraf.com").first()
    
    response = client.delete(f"/admin/users/{admin.id}", headers=admin_headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Cannot delete your own account" in response.json()["detail"]


def test_admin_promote_user(client, admin_headers, db_session):
    """Testa promoção de usuário a admin"""
    from proraf.models.user import User
    from proraf.security import get_password_hash
    
    user = User(
        nome="Regular User",
        email="regular@test.com",
        senha=get_password_hash("pass"),
        tipo_pessoa="F",
        cpf="12345678901",
        tipo_perfil="user"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    response = client.patch(f"/admin/users/{user.id}/promote", headers=admin_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["tipo_perfil"] == "admin"


def test_admin_promote_already_admin(client, admin_headers, db_session):
    """Testa promoção de usuário que já é admin"""
    from proraf.models.user import User
    from proraf.security import get_password_hash
    
    user = User(
        nome="Already Admin",
        email="alreadyadmin@test.com",
        senha=get_password_hash("pass"),
        tipo_pessoa="F",
        cpf="12345678901",
        tipo_perfil="admin"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    response = client.patch(f"/admin/users/{user.id}/promote", headers=admin_headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already an admin" in response.json()["detail"]


def test_admin_demote_user(client, admin_headers, db_session):
    """Testa rebaixamento de admin a usuário comum"""
    from proraf.models.user import User
    from proraf.security import get_password_hash
    
    user = User(
        nome="Admin to Demote",
        email="demote@test.com",
        senha=get_password_hash("pass"),
        tipo_pessoa="F",
        cpf="12345678901",
        tipo_perfil="admin"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    response = client.patch(f"/admin/users/{user.id}/demote", headers=admin_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["tipo_perfil"] == "user"


def test_admin_cannot_demote_self(client, admin_headers, db_session):
    """Testa que admin não pode rebaixar a si mesmo"""
    from proraf.models.user import User
    
    admin = db_session.query(User).filter(User.email == "admin@proraf.com").first()
    
    response = client.patch(f"/admin/users/{admin.id}/demote", headers=admin_headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Cannot demote yourself" in response.json()["detail"]


def test_admin_demote_regular_user(client, admin_headers, db_session):
    """Testa rebaixamento de usuário que não é admin"""
    from proraf.models.user import User
    from proraf.security import get_password_hash
    
    user = User(
        nome="Regular User",
        email="regulardemote@test.com",
        senha=get_password_hash("pass"),
        tipo_pessoa="F",
        cpf="12345678901",
        tipo_perfil="user"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    response = client.patch(f"/admin/users/{user.id}/demote", headers=admin_headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "not an admin" in response.json()["detail"]


def test_admin_get_users_stats(client, admin_headers, db_session):
    """Testa estatísticas de usuários"""
    from proraf.models.user import User
    from proraf.security import get_password_hash
    
    users = [
        User(nome="User PF 1", email="pf1@test.com", senha=get_password_hash("pass"), tipo_pessoa="F", cpf="11111111111", tipo_perfil="user"),
        User(nome="User PF 2", email="pf2@test.com", senha=get_password_hash("pass"), tipo_pessoa="F", cpf="22222222222", tipo_perfil="user"),
        User(nome="User PJ 1", email="pj1@test.com", senha=get_password_hash("pass"), tipo_pessoa="J", cnpj="11111111000111", tipo_perfil="user"),
        User(nome="Admin 2", email="admin2@test.com", senha=get_password_hash("pass"), tipo_pessoa="F", cpf="33333333333", tipo_perfil="admin"),
    ]
    for u in users:
        db_session.add(u)
    db_session.commit()
    
    response = client.get("/admin/users/stats/overview", headers=admin_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert "total_users" in data
    assert "total_admins" in data
    assert "total_regular_users" in data
    assert "total_pessoa_fisica" in data
    assert "total_pessoa_juridica" in data
    
    assert data["total_users"] >= 5
    assert data["total_admins"] >= 2
    assert data["total_pessoa_juridica"] >= 1


def test_regular_user_cannot_access_admin_endpoints(client, auth_headers):
    """Testa que usuário comum não pode acessar endpoints admin"""
    
    # Lista usuários
    response = client.get("/admin/users/", headers=auth_headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    
    # Buscar usuário
    response = client.get("/admin/users/1", headers=auth_headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    
    # Atualizar usuário
    response = client.put("/admin/users/1", json={"nome": "Test"}, headers=auth_headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    
    # Deletar usuário
    response = client.delete("/admin/users/1", headers=auth_headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    
    # Promover usuário
    response = client.patch("/admin/users/1/promote", headers=auth_headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    
    # Stats
    response = client.get("/admin/users/stats/overview", headers=auth_headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_pagination_admin_users(client, admin_headers, db_session):
    """Testa paginação na listagem de usuários"""
    from proraf.models.user import User
    from proraf.security import get_password_hash
    
    # Cria 25 usuários
    for i in range(25):
        user = User(
            nome=f"User {i}",
            email=f"user{i}@test.com",
            senha=get_password_hash("pass"),
            tipo_pessoa="F",
            cpf=f"{i:011d}"
        )
        db_session.add(user)
    db_session.commit()
    
    # Primeira página
    response = client.get("/admin/users/?skip=0&limit=10", headers=admin_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 10
    
    # Segunda página
    response = client.get("/admin/users/?skip=10&limit=10", headers=admin_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 10