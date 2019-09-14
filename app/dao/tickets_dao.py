from app.models import Ticket


def dao_get_tickets_for_order(order_id):
    return Ticket.query.filter_by(order_id=order_id).order_by(Ticket.created_at).all()
