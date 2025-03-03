import uuid
import jwt
from datetime import datetime, timedelta


class InternalTokenService:
    @staticmethod
    def generate_internal_token(secret, expiration_time_in_seconds, payload_obj):
        '''
        :param secret: This parameter receives a key to encrypt the payload data by using SHA256 algorithm.
        :param expiration_time_in_seconds: This parameter receives expiration time in seconds.
        :param payload_obj: This parameter receives the object whose data has to be encrypted. It should not be None.
        :return: It returns the encoded token.
        '''
        payload = vars(payload_obj)
        return JwtUtil.generate_internal_token(secret,
                                               expiration_time_in_seconds, payload)

    @staticmethod
    def generate_internal_token_for_dict(secret, expiration_time_in_seconds, payload):
        '''
        :param secret: This parameter receives a key to encrypt the payload data by using SHA256 algorithm.
        :param expiration_time_in_seconds: This parameter receives expiration time in seconds.
        :param payload: This parameter receives a dictionary whose data has to be encrypted.
        :return: It returns the encoded token.
        '''
        return JwtUtil.generate_internal_token(secret,
                                               expiration_time_in_seconds, payload)

    @staticmethod
    def validate_token(secret, token):
        '''
        :param secret: This parameter receives a key to decode and validate the payload data by using SHA256 algorithm.
        :param token: This parameter receives the token that has to be decoded and validated.
        :return: It returns the decoded data.
        '''
        return JwtUtil.validate_internal_token(secret, token)

    @staticmethod
    def generate_trace_id():
        '''
        :return: This returns a random uuid that can be used as request ID.
        '''
        return str(uuid.uuid4())


class JwtUtil:

    @staticmethod
    def generate_internal_token(secret: str, expiration_time_in_seconds: int, payload) -> str:
        """
        Generate a JWT token with user claims.

        :param secret: The secret key for signing the token.
        :param expiration_time_in_seconds: Token expiration time in seconds.
        :param user: An object representing the authenticated user (e.g., a Django model or serializer).
        :return: Encoded JWT token as a string.
        """
        current_time = datetime.utcnow()

        payload["iat"] = current_time
        payload["exp"] = current_time + timedelta(seconds=expiration_time_in_seconds)

        return jwt.encode(payload, secret, algorithm="HS256")

    @staticmethod
    def validate_internal_token(secret: str, token: str):
        """
        Validate a JWT token and decode its payload.

        :param secret: The secret key used for signing the token.
        :param token: The JWT token to validate.
        :return: Decoded payload as a dictionary.
        """
        try:
            decoded_token = jwt.decode(token, secret, algorithms=["HS256"])
            return decoded_token
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")
        except Exception as e:
            raise ValueError(f"Error occurred - {e}")