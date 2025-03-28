import json
from jinja2 import Environment, FileSystemLoader
import os 

# Load JSON data (replace with your actual file path or data)
json_data = [
    {
        "recipient": "8285027775",
        "messages": [
            "Stock of Jamun Masala- Discounted is expiring soon. Please take necessary action.",
            "The following retailers have not ordered in the last 3 weeks: Aman Pan Shop, Ankit store , Cake Break, Krishna general Store , Royal spoon cafe , Harish Bakery, The pan palace 119 noida, Majidul pan, S b mart bisrakh , Deepak pan shop bisrakh .",
            "These retailers were visited less than 4 times this month: The pan palace 119 noida (FE: Anil Kumar ), Majidul pan (FE: Anil Kumar ), Royal spoon cafe  (FE: Anil Kumar ), Deepak pan shop bisrakh  (FE: Anil Kumar ), Harish Bakery (FE: Anil Kumar ), Aman Pan Shop (FE: Anil Kumar ).",
            "Stock of Original Lemon Masala Juice is expiring soon. Please take necessary action.",
            "BeatPlan not assigned to Rohit, Raunak, Anish Kumar, Naina, Prakash Jha, Aneesh Singh, Anurag Tiwari, Asmit Agarwal, Manoj, Siddharth, Deepak, Sandeep singh, Sudhanshu Dixit, Aneesh Singh, Pranav, Goldy, Akash yadav, Aman, Sakshat, Sakina Khan, Arpit, Mukesh for today."
        ],
        "person_name": "Deepak",
        "role": "ASM"
    },
    {
        "recipient": "8447686869",
        "messages": [
            "Stock of Jamun Masala- Discounted is expiring soon. Please take necessary action.",
            "Stock of LZB Product is expiring soon. Please take necessary action.",
            "Stock of Original Lemon Masala Juice is expiring soon. Please take necessary action.",
            "BeatPlan not assigned to Vinay Singh, Anshuman for today."
        ],
        "person_name": "Siddharth Prakash",
        "role": "ASM"
    },
    {
        "recipient": "9916317375",
        "messages": [
            "Product: Headshot Classic Energy Drink 250ml, Last Sale: 2024-07-28\nProduct: Original Cummin Masala Juice, Last Sale: 2024-08-04\nProduct: FOMO Peach Iced Tea Premix 125ml, Last Sale: 2024-07-07\nProduct: Sour Cream Onion - 30G, Last Sale: 2024-03-08"
        ],
        "person_name": "Aneesh Singh",
        "role": "Field Executive"
    }
    # Add more recipients as per your full JSON data
]

# Set up Jinja2 environment
env = Environment(loader=FileSystemLoader('.'))
template = env.from_string("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Inventory and Sales Report - {{person_name}}</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            line-height: 1.6;
        }
        .container {
            max-width: 1000px;
            margin: 0 auto;
        }
        .header {
            text-align: center;
            border-bottom: 2px solid #333;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        .recipient-section {
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 15px;
        }
        .recipient-header {
            background-color: #f5f5f5;
            padding: 10px;
            border-radius: 3px;
            margin-bottom: 15px;
        }
        .recipient-header h2 {
            margin: 0;
            color: #333;
            font-size: 18px;
        }
        .recipient-info {
            font-size: 14px;
            color: #666;
            margin: 5px 0;
        }
        .messages-list {
            margin-left: 20px;
        }
        .message-item {
            margin-bottom: 10px;
            font-size: 14px;
        }
        .products-table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 15px;
        }
        .products-table th,
        .products-table td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        .products-table th {
            background-color: #f0f0f0;
            font-weight: bold;
        }
        .alert {
            color: #d32f2f;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Inventory and Sales Report</h1>
            <p>Date: March 28, 2025</p>
        </div>
        <div class="recipient-section">
            <div class="recipient-header">
                <h2>Recipient: {{recipient_phone}}</h2>
                <div class="recipient-info">Name: {{person_name}}</div>
                <div class="recipient-info">Role: {{role}}</div>
            </div>
            <div class="messages-list">
                {{messages_html | safe}}
            </div>
        </div>
    </div>
</body>
</html>
""")

# Function to generate messages HTML
def generate_messages_html(messages):
    messages_html = ""
    for message in messages:
        if "Product:" in message and "Last Sale:" in message:
            products = [line.split(', Last Sale:') for line in message.split('\n')]
            products_data = [{'product_name': p[0].replace('Product:', '').strip(), 
                            'last_sale_date': p[1].strip()} for p in products if len(p) == 2]
            messages_html += env.from_string("""
                <table class="products-table">
                    <thead><tr><th>Product Name</th><th>Last Sale Date</th></tr></thead>
                    <tbody>
                        {% for product in products %}
                        <tr><td>{{product.product_name}}</td><td>{{product.last_sale_date}}</td></tr>
                        {% endfor %}
                    </tbody>
                </table>
            """).render(products=products_data)
        else:
            messages_html += f'<div class="message-item {"alert" if "Alert:" in message else ""}">{message}</div>'
    return messages_html

# Generate separate HTML files for each recipient
for recipient in json_data:
    messages_html = generate_messages_html(recipient['messages'])
    html_content = template.render(
        recipient_phone=recipient['recipient'],
        person_name=recipient['person_name'],
        role=recipient['role'],
        messages_html=messages_html
    )
    
    pdf_parent_folder_path = "pdf" 
    output_filename = f"pdf/report_{recipient['recipient']}.html"
    
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"Generated HTML: {output_filename}")

print("All HTML files generated successfully!")