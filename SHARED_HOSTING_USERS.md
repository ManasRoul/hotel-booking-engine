# Creating Users on Shared Hosting

After deploying your Hotel Booking Engine, you need to create user accounts. Here's how to do it on shared hosting.

---

## 🌐 For Shared Hosting (cPanel/Bluehost/Hostinger)

Since you won't have direct Python REPL access on most shared hosting, here are your options:

---

## ✅ Method 1: Using phpMyAdmin (Easiest)

### Step 1: Access phpMyAdmin
1. Login to your **cPanel**
2. Find and click **"phpMyAdmin"** under Databases section

### Step 2: Select Your Database
1. On the left sidebar, click your database name (e.g., `username_hotel`)

### Step 3: Find Users Table
1. Click on the **`user`** table in the list

### Step 4: Insert New User
1. Click the **"Insert"** tab at the top
2. Fill in the form:

**For Owner/Admin:**
| Field | Value | Notes |
|-------|-------|-------|
| id | Leave empty | Auto-generated |
| username | `admin` | Choose your username |
| password_hash | See below | Must hash the password |
| color | `#667eea` | Hex color code (optional) |
| role | `owner` | Type exactly for admin access |

**For Regular User (Contributor):**
| Field | Value | Notes |
|-------|-------|-------|
| id | Leave empty | Auto-generated |
| username | `john` | Choose your username |
| password_hash | See below | Must hash the password |
| color | `#48bb78` | Hex color code (optional) |
| role | `contributor` | Type exactly for regular user |

### Step 5: Generate Password Hash

**Option A: Use Python (locally then copy hash)**
```bash
# On your local machine
python3 -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('your_password_here'))"
```

**Option B: Use Online Tool**
1. Go to: https://bcrypt-generator.com/
2. Enter your password (e.g., `SecurePass123!`)
3. Click "Generate Hash"
4. Copy the bcrypt hash
5. Paste into `password_hash` field

**Option C: Create a Temporary Hash Generator Page**

Create a file `create_hash.py` on your server:
```python
from werkzeug.security import generate_password_hash
import sys

if len(sys.argv) > 1:
    password = sys.argv[1]
    hash_pw = generate_password_hash(password)
    print(f"Password: {password}")
    print(f"Hash: {hash_pw}")
else:
    print("Usage: python create_hash.py your_password")
```

Run it:
```bash
source venv/bin/activate
python create_hash.py MyPassword123
```

### Step 6: Click "Go" to Insert

---

## 📝 Method 2: Using SQL Query in phpMyAdmin

### Step 1: Open SQL Tab
1. In phpMyAdmin, select your database
2. Click **"SQL"** tab at the top

### Step 2: Run SQL Command

**Create Owner (Admin):**
```sql
INSERT INTO user (username, password_hash, color, role) 
VALUES (
    'admin',
    'scrypt:32768:8:1$YourHashHere',
    '#667eea',
    'owner'
);
```

**Create Contributor:**
```sql
INSERT INTO user (username, password_hash, color, role) 
VALUES (
    'john',
    'scrypt:32768:8:1$YourHashHere',
    '#48bb78',
    'contributor'
);
```

⚠️ **Important:** Replace `YourHashHere` with actual password hash generated using one of the methods above.

---

## 🐍 Method 3: Using SSH Python Console (If Available)

If your host provides SSH access with Python:

### Step 1: SSH into your server
```bash
ssh username@yourhost.com
```

### Step 2: Navigate to app directory
```bash
cd ~/public_html  # or your app directory
```

### Step 3: Activate virtual environment
```bash
source venv/bin/activate
```

### Step 4: Run Python shell
```bash
python3
```

### Step 5: Create user in Python
```python
from app import app, db, User

# Create application context
with app.app_context():
    # Create owner/admin user
    admin = User(
        username='admin',
        role='owner',
        color='#667eea'
    )
    admin.set_password('your_secure_password')
    db.session.add(admin)
    
    # Create contributor user
    contributor = User(
        username='john',
        role='contributor',
        color='#48bb78'
    )
    contributor.set_password('johns_password')
    db.session.add(contributor)
    
    # Save to database
    db.session.commit()
    print('Users created successfully!')
```

### Step 6: Exit Python
```python
exit()
```

---

## 🔧 Method 4: Create User Script (Recommended for Multiple Users)

Create a file `create_user.py` in your app directory:

```python
#!/usr/bin/env python3
"""
Script to create users for Hotel Booking Engine
Usage: python create_user.py
"""

from app import app, db, User
import sys

def create_user():
    with app.app_context():
        print("=== Hotel Booking Engine - Create User ===\n")
        
        # Get user details
        username = input("Enter username: ").strip()
        
        # Check if user exists
        existing = User.query.filter_by(username=username).first()
        if existing:
            print(f"❌ Error: User '{username}' already exists!")
            return
        
        password = input("Enter password: ").strip()
        if len(password) < 6:
            print("❌ Error: Password must be at least 6 characters!")
            return
        
        role = input("Enter role (owner/contributor) [contributor]: ").strip() or "contributor"
        if role not in ['owner', 'contributor']:
            print("❌ Error: Role must be 'owner' or 'contributor'!")
            return
        
        color = input("Enter color code [#667eea]: ").strip() or "#667eea"
        
        # Create user
        new_user = User(
            username=username,
            role=role,
            color=color
        )
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        print(f"\n✅ User '{username}' created successfully!")
        print(f"   Role: {role}")
        print(f"   Color: {color}")

if __name__ == '__main__':
    try:
        create_user()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
```

**Usage:**
```bash
source venv/bin/activate
python create_user.py
```

---

## 👥 User Roles Explained

### Owner
- Full administrative access
- Can create, edit, and delete rooms
- Can manage all bookings
- Can create and delete users
- Can view all reports
- Can manage system settings

### Contributor
- Can create and edit bookings
- Can view room availability
- Can view their own bookings
- Cannot delete rooms or users
- Limited report access

---

## 🔐 Password Security Tips

1. **Use strong passwords:**
   - Minimum 8 characters
   - Mix of uppercase, lowercase, numbers, and symbols
   - Example: `B00k!ng#2024`

2. **Different passwords for different users**

3. **Change default passwords immediately after first login**

4. **Never share passwords via insecure channels**

---

## 📊 Verify Users Created

### Using phpMyAdmin:
1. Select your database
2. Click on `user` table
3. Click "Browse" tab
4. You should see your created users

### Using MySQL Command Line:
```bash
mysql -u your_user -p your_database -e "SELECT id, username, role FROM user;"
```

---

## ❓ Troubleshooting

### Issue: "Table 'user' doesn't exist"

The database tables weren't created. Run:
```bash
source venv/bin/activate
python3 -c "from app import app, db; app.app_context().push(); db.create_all()"
```

### Issue: Password doesn't work after creation

- Make sure you used `generate_password_hash()` from werkzeug
- Verify the hash was copied completely (no truncation)
- Try resetting the password using one of the methods above

### Issue: Cannot login as owner

- Verify role is exactly `owner` (lowercase)
- Check there are no extra spaces in the role field
- Confirm password hash was generated correctly

---

## 🎯 Quick Start Commands

```bash
# Activate environment
source venv/bin/activate

# Create admin user (quick method)
python3 -c "from app import app, db, User; app.app_context().push(); u = User(username='admin', role='owner'); u.set_password('admin123'); db.session.add(u); db.session.commit(); print('Admin created!')"

# List all users
python3 -c "from app import app, db, User; app.app_context().push(); print('Users:'); [print(f'- {u.username} ({u.role})') for u in User.query.all()]"
```

---

## ✅ Success!

Once you've created your users, you can login to your Hotel Booking Engine at:
`https://yourdomain.com/login`

Use the credentials you just created to access the system!

**Happy Booking! 🏨**
