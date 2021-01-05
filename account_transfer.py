import stripe

stripe.api_key = 'sk_test_51Hye8wIiHXHBpTjOvSAZG2BJD0P6NTSkBigo7SmvP14RsPDZAdcKN55qJbtOA9zDmScjtn2s2ufn4XIHWwnlkbve00d7A65C6o'

account = stripe.Account.create(
  country='US',
  type='custom',
  capabilities={
    'card_payments': {
      'requested': True,
    },
    'transfers': {
      'requested': True,
    },
  },
)