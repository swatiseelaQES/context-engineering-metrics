# Orders API Contract

GET /orders/{id}

Response fields:
- id: string
- status: paid | pending | failed | settled
- total: number
- currency: ISO-4217 string

The `settled` status means payment has cleared and reconciliation is complete.
