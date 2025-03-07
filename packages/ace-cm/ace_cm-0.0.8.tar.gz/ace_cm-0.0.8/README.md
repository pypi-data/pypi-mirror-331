# ACE Cookie Manager

Access and change browser cookies from Streamlit scripts:

```python
import os
import streamlit as st
from ace_cm import ECM

# This should be on top of your script
cookies = ECM(
    prefix="ace/ace-cm/",
    password=os.environ.get("COOKIES_PASSWORD", "My secret password"),
)
if not cookies.ready():
    st.stop()

st.write("Current cookies:", cookies)
value = st.text_input("New value for a cookie")
if st.button("Change the cookie"):
    cookies['a-cookie'] = value  # This will get saved on next rerun
    if st.button("No really, change it now"):
        cookies.save()  # Force saving the cookies now, without a rerun
```

---

## Required Variables

CLIENT_ID=\*\*\*
CLIENT_SECRET=\*\*\*
AZURE_TENANT_ID=\*\*\*
AUTHORITY=\*\*\*
REDIRECT_URI=\*\*\*

---
