from fpdf import FPDF

# আগে install করো
# pip install fpdf2

pdf = FPDF()
pdf.add_page()
pdf.set_font("Helvetica", size=12)

content = """
Tasty Bites Restaurant - Customer Information Guide

About Us:
Tasty Bites is a well-known family-friendly restaurant located in Uttara, Dhaka.
Since 2012, we have been offering a mix of traditional Bengali and modern fusion cuisine.
Our chefs are highly skilled and focus on quality, hygiene, and authentic taste.

Menu and Prices:

Mutton Kacchi Biryani: 380 taka per plate
Chicken Biryani: 250 taka per plate
Beef Kala Bhuna: 300 taka per plate
Grilled Chicken: 320 taka per plate
Prawn Masala: 400 taka per plate
Mixed Vegetable Curry: 180 taka per plate
Plain Rice: 50 taka per plate

Opening Hours:

Sunday to Thursday: 10:00 AM - 10:30 PM
Friday: 2:00 PM - 11:30 PM
Saturday: 9:00 AM - 11:00 PM

Delivery Information:
We provide fast and reliable home delivery within Dhaka city.

Minimum order: 400 taka
Delivery charge: 60 taka
Estimated delivery time: 25-40 minutes
Hotline: 01737-233015

Special Offers:

Weekend Deal: Buy 2 biryanis, get 1 soft drink free
Student Discount: 10% off with valid ID
Family Combo Package: Starting from 1200 taka
Event Catering available for weddings, parties, and corporate events

Facilities:

Air-conditioned dining space
Free Wi-Fi
Online payment (bKash, Nagad, Card)
Parking available

Location:
House 12, Sector 7, Uttara, Dhaka-1230
Near Uttara Lake Park, beside Dutch-Bangla Ban
"""

for line in content.split('\n'):
    pdf.cell(0, 8, line, ln=True)

pdf.output("restaurant_guide.pdf")
print("PDF created!")