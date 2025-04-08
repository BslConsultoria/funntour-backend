from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from sqlalchemy import select, update, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import bcrypt

from app.models.usuario import Usuario
from app.models.endereco import Endereco
from app.models.cidade import Cidade
from app.models.perfil import Perfil
import logging

logger = logging.getLogger(__name__)

class UsuarioService:
    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Usuario]:
        """
        Retorna todos os usuários não excluídos, incluindo endereço e perfil.
        """
        query = select(Usuario).where(Usuario.dt_exclusao.is_(None))
        # Carrega relacionamentos aninhados para permitir acesso a cidade.estado.pais
        query = query.options(
            selectinload(Usuario.endereco).selectinload(Endereco.cidade).selectinload(Cidade.estado),
            selectinload(Usuario.perfil)
        )
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_by_id(db: AsyncSession, usuario_id: int) -> Optional[Usuario]:
        """
        Retorna um usuário pelo ID se não estiver excluído, incluindo endereço e perfil.
        """
        query = select(Usuario).where(
            and_(
                Usuario.id == usuario_id,
                Usuario.dt_exclusao.is_(None)
            )
        )
        query = query.options(
            selectinload(Usuario.endereco),
            selectinload(Usuario.perfil)
        )
        result = await db.execute(query)
        return result.scalars().first()
    
    @staticmethod
    async def get_by_cpf_cnpj(db: AsyncSession, cpf_cnpj: str) -> Optional[Usuario]:
        """
        Busca um usuário pelo CPF/CNPJ.
        """
        # Remove caracteres não numéricos para comparação
        cpf_cnpj_numerico = ''.join(filter(str.isdigit, cpf_cnpj))
        
        # Primeiro tentamos buscar o CPF/CNPJ exato
        query = select(Usuario).where(
            and_(
                Usuario.cpf_cnpj == cpf_cnpj,
                Usuario.dt_exclusao.is_(None)
            )
        )
        query = query.options(
            selectinload(Usuario.endereco),
            selectinload(Usuario.perfil)
        )
        result = await db.execute(query)
        usuario = result.scalars().first()
        
        if usuario:
            return usuario
            
        # Se não encontrou, busca todos os usuários e compara manualmente
        query = select(Usuario).where(Usuario.dt_exclusao.is_(None))
        # Carrega relacionamentos aninhados para permitir acesso a cidade.estado.pais
        query = query.options(
            selectinload(Usuario.endereco).selectinload(Endereco.cidade).selectinload(Cidade.estado),
            selectinload(Usuario.perfil)
        )
        result = await db.execute(query)
        usuarios = result.scalars().all()
        
        # Filtra manualmente os usuários com CPF/CNPJ correspondente
        for usuario in usuarios:
            usuario_cpf_cnpj = ''.join(filter(str.isdigit, usuario.cpf_cnpj))
            if usuario_cpf_cnpj == cpf_cnpj_numerico:
                return usuario
        
        return None
    
    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> Optional[Usuario]:
        """
        Busca um usuário pelo e-mail.
        """
        if not email:
            return None
            
        query = select(Usuario).where(
            and_(
                func.lower(Usuario.email) == email.lower(),
                Usuario.dt_exclusao.is_(None)
            )
        )
        query = query.options(
            selectinload(Usuario.endereco),
            selectinload(Usuario.perfil)
        )
        result = await db.execute(query)
        return result.scalars().first()
    
    @staticmethod
    def _hash_password(senha: str) -> str:
        """
        Criptografa a senha utilizando bcrypt.
        """
        # Gera o salt e criptografa a senha
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(senha.encode('utf-8'), salt)
        return hashed_password.decode('utf-8')
    
    @staticmethod
    def _verify_password(senha_plana: str, senha_hash: str) -> bool:
        """
        Verifica se a senha fornecida corresponde ao hash armazenado.
        """
        return bcrypt.checkpw(senha_plana.encode('utf-8'), senha_hash.encode('utf-8'))

    @staticmethod
    async def authenticate_user(db: AsyncSession, cpf_cnpj: str, senha: str) -> Optional[Usuario]:
        """
        Autentica um usuário com CPF/CNPJ e senha.
        """
        usuario = await UsuarioService.get_by_cpf_cnpj(db, cpf_cnpj)
        if not usuario:
            return None
        
        if not UsuarioService._verify_password(senha, usuario.senha):
            return None
            
        return usuario

    @staticmethod
    async def create(db: AsyncSession, usuario_data: Dict[str, Any]) -> Usuario:
        """
        Cria um novo usuário junto com seu endereço.
        """
        # Verifica se já existe um usuário com o mesmo CPF/CNPJ
        existing_user = await UsuarioService.get_by_cpf_cnpj(db, usuario_data["cpf_cnpj"])
        if existing_user:
            raise ValueError(f"Já existe um usuário cadastrado com o CPF/CNPJ '{usuario_data['cpf_cnpj']}'")
        
        # Verifica se já existe um usuário com o mesmo email, se fornecido
        if "email" in usuario_data and usuario_data["email"]:
            existing_email = await UsuarioService.get_by_email(db, usuario_data["email"])
            if existing_email:
                raise ValueError(f"Já existe um usuário cadastrado com o e-mail '{usuario_data['email']}'")
        
        # Cria o endereço primeiro (sempre presente conforme schema)
        endereco_data = usuario_data.pop('endereco')
        # Cria o endereço
        db_endereco = Endereco(**endereco_data)
        db.add(db_endereco)
        await db.flush()  # Para obter o ID sem commit
        
        # Usa o ID do endereço para o usuário
        usuario_data['endereco_id'] = db_endereco.id
        
        # Criptografa a senha antes de armazenar
        if "senha" in usuario_data:
            usuario_data["senha"] = UsuarioService._hash_password(usuario_data["senha"])
        
        # Cria o novo usuário
        db_usuario = Usuario(**usuario_data)
        db.add(db_usuario)
        await db.commit()
        await db.refresh(db_usuario)
        
        # Retorna o usuário diretamente
        return db_usuario

    @staticmethod
    async def update(db: AsyncSession, usuario_id: int, usuario_data: Dict[str, Any]) -> Optional[Usuario]:
        """
        Atualiza um usuário existente e seu endereço, se fornecido.
        """
        # Verifica se o usuário existe
        db_usuario = await UsuarioService.get_by_id(db, usuario_id)
        if not db_usuario:
            return None
        
        # Verifica se está alterando o CPF/CNPJ e se já existe outro usuário com esse CPF/CNPJ
        if "cpf_cnpj" in usuario_data and usuario_data["cpf_cnpj"] != db_usuario.cpf_cnpj:
            existing_user = await UsuarioService.get_by_cpf_cnpj(db, usuario_data["cpf_cnpj"])
            if existing_user and existing_user.id != usuario_id:
                raise ValueError(f"Já existe um usuário cadastrado com o CPF/CNPJ '{usuario_data['cpf_cnpj']}'")
        
        # Verifica se está alterando o email e se já existe outro usuário com esse email
        if "email" in usuario_data and usuario_data["email"] and usuario_data["email"] != db_usuario.email:
            existing_email = await UsuarioService.get_by_email(db, usuario_data["email"])
            if existing_email and existing_email.id != usuario_id:
                raise ValueError(f"Já existe um usuário cadastrado com o e-mail '{usuario_data['email']}'")
        
        # Se dados de endereço estão presentes, atualiza o endereço
        endereco_data = usuario_data.pop('endereco', None)
        if endereco_data:
            if db_usuario.endereco_id:
                # Atualiza o endereço existente
                endereco_update = update(Endereco).where(Endereco.id == db_usuario.endereco_id).values(**endereco_data)
                await db.execute(endereco_update)
            else:
                # Cria um novo endereço se o usuário não tinha um
                db_endereco = Endereco(**endereco_data)
                db.add(db_endereco)
                await db.flush()
                # Adiciona o ID do novo endereço ao usuário
                usuario_data['endereco_id'] = db_endereco.id
        
        # Criptografa a senha se estiver sendo alterada
        if "senha" in usuario_data and usuario_data["senha"]:
            usuario_data["senha"] = UsuarioService._hash_password(usuario_data["senha"])
        
        # Atualiza o usuário
        update_stmt = update(Usuario).where(Usuario.id == usuario_id).values(**usuario_data)
        await db.execute(update_stmt)
        await db.commit()
        
        # Retorna o usuário atualizado com relacionamentos
        return await UsuarioService.get_by_id(db, usuario_id)

    @staticmethod
    async def delete(db: AsyncSession, usuario_id: int) -> bool:
        """
        Exclui logicamente um usuário.
        """
        db_usuario = await UsuarioService.get_by_id(db, usuario_id)
        if not db_usuario:
            return False

        # Exclusão lógica
        update_stmt = update(Usuario).where(Usuario.id == usuario_id).values(dt_exclusao=datetime.now())
        await db.execute(update_stmt)
        await db.commit()
        return True
        
    @staticmethod
    async def change_password(db: AsyncSession, usuario_id: int, senha_atual: str, nova_senha: str) -> bool:
        """
        Altera a senha de um usuário, verificando a senha atual.
        """
        db_usuario = await UsuarioService.get_by_id(db, usuario_id)
        if not db_usuario:
            return False
        
        # Verifica se a senha atual está correta
        if not UsuarioService._verify_password(senha_atual, db_usuario.senha):
            raise ValueError("Senha atual incorreta")
        
        # Criptografa a nova senha
        senha_hash = UsuarioService._hash_password(nova_senha)
        
        # Atualiza a senha
        update_stmt = update(Usuario).where(Usuario.id == usuario_id).values(senha=senha_hash)
        await db.execute(update_stmt)
        await db.commit()
        return True
    
    @staticmethod
    async def reset_password(db: AsyncSession, usuario_id: int, nova_senha: str) -> bool:
        """
        Redefine a senha de um usuário sem verificar a senha atual.
        Usado após validação de token de recuperação.
        """
        db_usuario = await UsuarioService.get_by_id(db, usuario_id)
        if not db_usuario:
            return False
        
        # Criptografa a nova senha
        senha_hash = UsuarioService._hash_password(nova_senha)
        
        # Atualiza a senha
        update_stmt = update(Usuario).where(Usuario.id == usuario_id).values(senha=senha_hash)
        await db.execute(update_stmt)
        await db.commit()
        return True
    
    @staticmethod
    async def find_user_by_credential(db: AsyncSession, credential: str) -> Optional[Usuario]:
        """
        Busca um usuário pelo CPF/CNPJ ou email.
        """
        # Tenta buscar por CPF/CNPJ
        usuario = await UsuarioService.get_by_cpf_cnpj(db, credential)
        if not usuario:
            # Se não encontrar, tenta buscar por email
            usuario = await UsuarioService.get_by_email(db, credential)
        return usuario
    
    @staticmethod
    async def generate_password_reset_token(db: AsyncSession, credential: str) -> Optional[Dict[str, Any]]:
        """
        Gera um token para recuperação de senha quando o usuário informa CPF/CNPJ ou email.
        Retorna um dicionário com o token, dados do usuário e timestamp de expiração.
        """
        import jwt
        import secrets
        from datetime import datetime, timedelta
        
        # Busca o usuário pelo CPF/CNPJ ou email
        usuario = await UsuarioService.find_user_by_credential(db, credential)
        if not usuario:
            return None
            
        # Gera um token único
        expiration = datetime.utcnow() + timedelta(minutes=10)
        
        # Dados a serem codificados no token
        token_data = {
            "sub": str(usuario.id),
            "exp": expiration.timestamp(),
            "jti": secrets.token_hex(8)  # ID único para este token
        }
        
        # Gera o token JWT usando o segredo da aplicação
        # Em produção, deve-se usar um segredo forte e configurável
        SECRET_KEY = "funntour-app-secret-key"  # Em produção, use variáveis de ambiente
        token = jwt.encode(token_data, SECRET_KEY, algorithm="HS256")
        
        return {
            "token": token,
            "usuario": {
                "id": usuario.id,
                "nome": usuario.nome,
                "cpf_cnpj": usuario.cpf_cnpj,
                "email": usuario.email,
                "whatsapp": usuario.whatsapp
            },
            "expira_em": expiration.isoformat()
        }
    
    @staticmethod
    def verify_password_reset_token(token: str) -> Optional[int]:
        """
        Verifica se um token de recuperação de senha é válido.
        Retorna o ID do usuário se o token for válido, None caso contrário.
        """
        import jwt
        from datetime import datetime
        
        try:
            # Decodifica o token JWT usando o segredo da aplicação
            SECRET_KEY = "funntour-app-secret-key"  # Em produção, use variáveis de ambiente
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            
            # Verifica se o token já expirou
            expiration = datetime.fromtimestamp(payload["exp"])
            if datetime.utcnow() > expiration:
                return None
                
            # Retorna o ID do usuário
            return int(payload["sub"])
        except (jwt.PyJWTError, ValueError, KeyError):
            return None
