import panel as pn
import pandas as pd
from datetime import date

pn.extension('tabulator', sizing_mode="stretch_width")  # Do NOT set template here
# ------------------------
# Globals and data holders
# ------------------------
user_list = ["Alice", "Bob", "Charlie", "Admin"]
timesheet_data = pd.DataFrame(columns=[
    "User", "Task", "Project Code", "Category", "Work Type",
    "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Total"
])

# ------------------------
# Widgets
# ------------------------
current_user = pn.widgets.Select(name="Select User", options=user_list)

job_desc = pn.widgets.TextInput(name="Job Description / Task")
project_code = pn.widgets.TextInput(name="Project Code")
category = pn.widgets.Select(name="Category", options=["Internal", "Customer", "Training"])
work_type = pn.widgets.Select(name="Work Type", options=["Design", "Review", "Testing", "Documentation"])

mon = pn.widgets.IntInput(name="Monday", value=0, start=0, end=24)
tue = pn.widgets.IntInput(name="Tuesday", value=0, start=0, end=24)
wed = pn.widgets.IntInput(name="Wednesday", value=0, start=0, end=24)
thu = pn.widgets.IntInput(name="Thursday", value=0, start=0, end=24)
fri = pn.widgets.IntInput(name="Friday", value=0, start=0, end=24)
sat = pn.widgets.IntInput(name="Saturday", value=0, start=0, end=24)

submit_btn = pn.widgets.Button(name="Submit Entry", button_type="primary")
status = pn.pane.Markdown("", sizing_mode="stretch_width")

# ------------------------
# Callback
# ------------------------
def submit_entry(event):
    total = sum([mon.value, tue.value, wed.value, thu.value, fri.value, sat.value])
    new_row = pd.DataFrame({
        "User": [current_user.value],
        "Task": [job_desc.value],
        "Project Code": [project_code.value],
        "Category": [category.value],
        "Work Type": [work_type.value],
        "Mon": [mon.value],
        "Tue": [tue.value],
        "Wed": [wed.value],
        "Thu": [thu.value],
        "Fri": [fri.value],
        "Sat": [sat.value],
        "Total": [total]
    })
    global timesheet_data
    timesheet_data = pd.concat([timesheet_data, new_row], ignore_index=True)
    status.object = f"✅ Entry added for {current_user.value}"
    clear_form()

def clear_form():
    job_desc.value = ""
    project_code.value = ""
    category.value = "Internal"
    work_type.value = "Design"
    for day in [mon, tue, wed, thu, fri, sat]:
        day.value = 0

submit_btn.on_click(submit_entry)

# ------------------------
# My Entries Table
# ------------------------
def get_user_entries():
    return timesheet_data[timesheet_data["User"] == current_user.value]

def update_table(event=None):
    table.value = get_user_entries()

table = pn.widgets.Tabulator(get_user_entries(), height=250)
current_user.param.watch(update_table, "value")

# ------------------------
# Admin Upload
# ------------------------
file_input = pn.widgets.FileInput(accept=".xlsx")
admin_status = pn.pane.Markdown("", sizing_mode="stretch_width")

def handle_upload(event):
    if current_user.value != "Admin":
        admin_status.object = "⚠️ Only Admin can upload files."
        return
    try:
        excel = pd.read_excel(file_input.filename, engine="openpyxl")
        excel["User"] = "Uploaded"
        global timesheet_data
        timesheet_data = pd.concat([timesheet_data, excel], ignore_index=True)
        admin_status.object = "✅ Excel uploaded and parsed."
    except Exception as e:
        admin_status.object = f"❌ Failed to upload: {e}"

file_input.param.watch(handle_upload, 'value')

# ------------------------
# Layout
# ------------------------
form = pn.Column(
    pn.pane.Markdown("## 📝 Timesheet Entry Form"),
    current_user,
    job_desc, project_code, category, work_type,
    pn.Row(mon, tue, wed),
    pn.Row(thu, fri, sat),
    submit_btn, status
)

entries = pn.Column(
    pn.pane.Markdown("## 📋 My Entries"),
    table
)

upload = pn.Column(
    pn.pane.Markdown("## 📤 Admin Excel Upload"),
    file_input,
    admin_status
)

main_tabs = pn.Tabs(
    ("Timesheet", form),
    ("My Entries", entries),
    ("Admin Upload", upload)
)

# ------------------------
# Bootstrap Dark Template
# ------------------------
template = pn.template.BootstrapTemplate(
    title="Timesheet Web App",
    theme="dark"  # Only 'default' and 'dark' are valid
)

template.main.append(main_tabs)
template.servable()
print("Tabs created:", main_tabs)
