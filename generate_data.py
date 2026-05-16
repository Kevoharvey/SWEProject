import os
import shutil
import glob
import MySQLdb
from werkzeug.security import generate_password_hash
import random

# Source images path (from the agent's brain directory)
src_dir = r"/Users/kevinharvey/Desktop/Projects/SWE Project/SWEProject/brain/395e8395-e810-407f-b359-48aefd1e7332"
project_dir = r"/Users/kevinharvey/Desktop/Projects/SWE Project/SWEProject"

# Directories
products_dir = os.path.join(project_dir, 'static', 'uploads', 'products')
profiles_dir = os.path.join(project_dir, 'static', 'uploads', 'profiles')
os.makedirs(products_dir, exist_ok=True)
os.makedirs(profiles_dir, exist_ok=True)

# Copy images to static folders
image_map = {}
for file in glob.glob(os.path.join(src_dir, "*.png")):
    basename = os.path.basename(file)
    name = basename.split('_')[0]
    
    if name.startswith('farmer'):
        dest = os.path.join(profiles_dir, basename)
        shutil.copy2(file, dest)
        image_map[name] = f"uploads/profiles/{basename}"
    else:
        dest = os.path.join(products_dir, basename)
        shutil.copy2(file, dest)
        image_map[name] = f"uploads/products/{basename}"

db = MySQLdb.connect(host="127.0.0.1", user="root", password="", database="farmers_market")
cur = db.cursor()

# 1. Add 10 Farmers
farmers_data = [
    ("John Appleseed", "john@appleseed.com", "Appleseed Orchards", "farmer1"),
    ("Mary Smith", "mary@smithfarms.com", "Smith Family Farms", "farmer2"),
    ("Robert Brown", "robert@brown.com", "Brown's Organic", "farmer3"),
    ("Sarah Green", "sarah@greenvalley.com", "Green Valley Farms", "farmer2"),
    ("David Miller", "david@miller.com", "Miller's Meat & Dairy", "farmer1"),
    ("Emma White", "emma@white.com", "White's Honey & Herbs", "farmer2"),
    ("James Wilson", "james@wilson.com", "Wilson Fresh Produce", "farmer3"),
    ("Linda Davis", "linda@davis.com", "Davis Family Bakery", "farmer2"),
    ("Michael Taylor", "michael@taylor.com", "Taylor's Free Range", "farmer1"),
    ("Barbara Moore", "barbara@moore.com", "Moore's Floral & Greens", "farmer2"),
]

farmer_ids = []
pw_hash = generate_password_hash('password123')

for full_name, email, farm_name, img_key in farmers_data:
    cur.execute("SELECT id FROM users WHERE email=%s", (email,))
    res = cur.fetchone()
    if res:
        user_id = res[0]
    else:
        cur.execute("INSERT INTO users (full_name, email, password_hash, role) VALUES (%s, %s, %s, 'farmer')",
                    (full_name, email, pw_hash))
        user_id = cur.lastrowid
        
        profile_img = image_map.get(img_key)
        cur.execute("""INSERT INTO farmers (user_id, farm_name, description, address, status, profile_image) 
                       VALUES (%s, %s, 'Local organic farm providing fresh products daily.', '123 Farm Rd, Valley', 'approved', %s)""",
                    (user_id, farm_name, profile_img))
        
        cur.execute("SELECT id FROM farmers WHERE user_id=%s", (user_id,))
        farmer_ids.append(cur.fetchone()[0])

db.commit()

# Get farmer IDs if they already existed
if not farmer_ids:
    cur.execute("SELECT id FROM farmers LIMIT 10")
    farmer_ids = [row[0] for row in cur.fetchall()]

# 2. Add 20 Products
products_data = [
    ("Red Tomatoes", "Vegetables", 3.50, "kg", "tomato", "Freshly picked organic red tomatoes."),
    ("Gala Apples", "Fruits", 4.00, "kg", "apple", "Crisp and sweet Gala apples."),
    ("Brown Eggs", "Eggs", 5.00, "dozen", "egg", "Free range organic brown eggs."),
    ("Wildflower Honey", "Honey", 12.00, "jar", "honey", "Raw wildflower honey straight from our hives."),
    ("Grass-fed Beef Steak", "Meat", 25.00, "kg", "beef", "Premium grass-fed beef cuts."),
    ("Artisan Cheddar", "Dairy", 8.50, "item", "cheese", "Aged artisan cheddar cheese block."),
    ("Organic Carrots", "Vegetables", 2.50, "bunch", "carrot", "Sweet orange carrots with tops."),
    ("Fresh Strawberries", "Fruits", 6.00, "item", "strawberry", "Sweet and juicy fresh strawberries."),
    ("Sourdough Bread", "Baked Goods", 7.00, "item", "bread", "Freshly baked artisan sourdough loaf."),
    ("Mixed Floral Bouquet", "Flowers", 15.00, "item", "flower", "Beautiful freshly cut farm flowers."),
    
    # Add variations to reach 20
    ("Cherry Tomatoes", "Vegetables", 4.50, "kg", "tomato", "Sweet little cherry tomatoes."),
    ("Granny Smith Apples", "Fruits", 3.80, "kg", "apple", "Tart and crisp green apples."),
    ("White Eggs", "Eggs", 4.50, "dozen", "egg", "Farm fresh white eggs."),
    ("Clover Honey", "Honey", 11.00, "jar", "honey", "Smooth clover honey."),
    ("Ground Beef", "Meat", 15.00, "kg", "beef", "Lean ground beef from grass-fed cows."),
    ("Goat Cheese", "Dairy", 9.00, "item", "cheese", "Creamy organic goat cheese."),
    ("Rainbow Carrots", "Vegetables", 3.50, "bunch", "carrot", "Colorful heirloom carrots."),
    ("Strawberry Jam", "Preserves", 6.50, "jar", "strawberry", "Homemade strawberry preserve."),
    ("Whole Wheat Bread", "Baked Goods", 6.00, "item", "bread", "Nutritious whole wheat loaf."),
    ("Sunflowers", "Flowers", 12.00, "item", "flower", "Bright and sunny fresh sunflowers.")
]

for name, category, price, unit, img_key, desc in products_data:
    farmer_id = random.choice(farmer_ids)
    cur.execute("""INSERT INTO products (farmer_id, name, category, description, price, quantity, unit, stock_status, is_active)
                   VALUES (%s, %s, %s, %s, %s, 100, %s, 'in-stock', 1)""",
                (farmer_id, name, category, desc, price, unit))
    product_id = cur.lastrowid
    
    photo_path = image_map.get(img_key)
    if photo_path:
        cur.execute("INSERT INTO product_photos (product_id, photo_path, display_order) VALUES (%s, %s, 0)",
                    (product_id, photo_path))

db.commit()
cur.close()
db.close()

print("Successfully seeded 10 farmers and 20 products with photos!")
