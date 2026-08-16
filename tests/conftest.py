"""
Pytest configuration and fixtures for creating IMAP objects
"""
import pytest
import sys

sys.path.insert(0, 'jobparser/')

@pytest.fixture(scope='function')
def create_msclient():
    """
    Factory fixture for creating IMAPHotmail objects.
    Returns session_id string for querying in tests.
    """
    from ms import IMAPMSClient

    def _create_msclient():
        """
        Create a IMAPHotmail with defaults.

        Args:
            None
        Returns:
            obj: iIMAPHotmailClient
        """
        msclient = IMAPMSClient(
        )
        return msclient

    return _create_msclient

# Ensure project root is in path
# left as a reminder to do this when we dockerise later


# commented for ease of future cribbing
# @pytest.fixture(scope='function')
# def db_session(app):
#     """
#     Function-scoped database session.
#     Each test gets a clean transaction that's rolled back after.
#     """
#     from gonnaenosaythat_app.extensions import db
#     from sqlalchemy.orm import sessionmaker, scoped_session

#     with app.app_context():
#         # Begin a nested transaction
#         connection = db.engine.connect()
#         transaction = connection.begin()

#         # Create a scoped session bound to this connection
#         session_factory = sessionmaker(bind=connection)
#         Session = scoped_session(session_factory)
#         session = Session()

#         # Replace the app's session with our transactional session
#         old_session = db.session
#         db.session = Session

#         yield session

#         # Rollback transaction
#         db.session = old_session
#         Session.remove()
#         transaction.rollback()
#         connection.close()


# commented out for when we come to take payment later.
# @pytest.fixture(scope='function')
# def create_payment(app):
#     """
#     factory fixture for creating payment objects.
#     returns payment id for querying in tests.
#     """
#     from models import payment
#     from gonnaenosaythat_app.extensions import db
#     from decimal import decimal

#     def _create_payment(email=none, status='pending', amount_gbp=50.00, **kwargs):
#         """
#         create a payment record.

#         args:
#             email: email address
#             status: payment status (default: 'pending')
#             amount_gbp: amount in gbp (default: 50.00)
#             **kwargs: additional fields

#         returns:
#             int: the payment id
#         """
#         with app.app_context():
#             if email is none:
#                 email = f"test_{generate_random_token(4)}@example.com"

#             stripe_session_id = kwargs.pop('stripe_session_id', f"cs_test_{generate_random_token(16)}")
#             currency = kwargs.pop('currency', 'gbp')
#             amount_charged = kwargs.pop('amount_charged', amount_gbp)

#             payment = payment(
#                 stripe_session_id=stripe_session_id,
#                 email=email,
#                 amount_gbp=decimal(str(amount_gbp)),
#                 currency=currency,
#                 amount_charged=decimal(str(amount_charged)),
#                 status=status,
#                 paid_at=datetime.utcnow() if status == 'paid' else none,
#                 **kwargs
#             )
#             db.session.add(payment)
#             db.session.commit()
#             return payment.id

#     return _create_payment


# @pytest.fixture(scope='function')
# def test_email():
#     """generate a unique test email for each test."""
#     return f"test_{generate_random_token(4)}@example.com"
