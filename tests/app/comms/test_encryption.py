from app.comms.encryption import encrypt, decrypt, get_tokens

sample_tokens = "memberid=123-456&typeid=test"
sample_salt = "test"
sample_enc = "GQAeFhEXGhBJVEFHWVFGQlIRCgQRDBdJAAAAAA=="


class WhenUsingEncryption:
    def it_encrypts_key_value(self, app):
        enc = encrypt(sample_tokens, sample_salt)
        assert enc == sample_enc

    def it_decrypts_code(self, app):
        dec = decrypt(sample_enc, sample_salt)
        assert dec == sample_tokens

    def it_gets_tokens(self, app):
        tokens = get_tokens(sample_tokens)

        assert tokens == {'memberid': '123-456', 'typeid': 'test'}

    def it_ignores_invalid_tokens(self, app):
        tokens = get_tokens(sample_tokens + '&invalid=x')

        assert tokens == {'memberid': '123-456', 'typeid': 'test'}
        assert 'invalid' not in tokens.keys()
