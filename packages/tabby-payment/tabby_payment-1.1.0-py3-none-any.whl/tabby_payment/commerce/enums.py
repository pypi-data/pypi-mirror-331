from enum import Enum


class OrderServiceStatus(Enum):
    new = 'new'
    processing = 'processing'
    completed = 'complete'
    refunded = 'refunded'
    canceled = 'canceled'
    unknown = 'unknown'



class OrderCommerceStatus(Enum):
    cancellation_waiting = '50'
    cancelled = '100'
    waiting = '200'
    payment_waiting = '300'
    confirmation_waiting = '350'
    approved = '400'
    preparing = '450'
    shipped = '500'
    shipped_and_informed = '510'
    ready_for_pickup = '520'
    attempted_delivery = '540'
    review_started = '544'
    review_waiting = '545'
    waiting_for_payment = '546'  # for trade-in status
    paid = '547'  # for trade-in status
    delivered = '550'
    refunded = '600'
