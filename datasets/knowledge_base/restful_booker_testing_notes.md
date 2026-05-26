# Restful Booker API Testing Notes

Restful Booker is a public API used for practicing API testing.

Useful API test generation rules:

- POST /booking should send Content-Type: application/json.
- A valid booking payload includes firstname, lastname, totalprice, depositpaid, bookingdates, and additionalneeds.
- bookingdates should include checkin and checkout.
- A successful create booking response includes bookingid and booking.
- Generated pytest tests should assert response status code and important response fields.
- Tests should avoid depending on exact bookingid values because IDs are generated dynamically.