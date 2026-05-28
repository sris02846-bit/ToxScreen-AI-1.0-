with open('app.py', 'r') as f:
    content = f.read()

# Find the pk_dashboard_page function and replace it with a working version
old_pk_start = "def pk_dashboard_page(username, tier):"
old_pk_end = "    st.markdown('</div>', unsafe_allow_html=True)\n\n"

# Find the actual function
if old_pk_start in content:
    print("Found PK Dashboard function")
else:
    print("PK Dashboard function not found!")

