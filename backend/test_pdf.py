from jobs.reports import generate_monthly_report
from app import app

with app.app_context():
    print("=== Testing PDF Generation for User ID 1 ===")
    
    # Generate PDF for user ID 1 (who has data)
    pdf_path = generate_monthly_report(user_id=1)
    
    if pdf_path:
        print(f"✅ PDF generated successfully: {pdf_path}")
        print("📄 PDF should show parking data for Manav Chawla")
    else:
        print("❌ PDF generation failed")
    
    print("\n=== Testing PDF Generation for User ID 2 ===")
    
    # Generate PDF for user ID 2 (who also has data)
    pdf_path2 = generate_monthly_report(user_id=2)
    
    if pdf_path2:
        print(f"✅ PDF generated successfully: {pdf_path2}")
        print("📄 PDF should show parking data for scrapper")
    else:
        print("❌ PDF generation failed") 