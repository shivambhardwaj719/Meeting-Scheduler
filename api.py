import frappe
from frappe import _
from frappe.utils import nowdate, add_days

def send_invitation_emails(meeting):
    """
    Send invitation emails to meeting attendees.

    Args:
        meeting (str): Meeting name

    Returns:
        None
    """
    meeting = frappe.get_doc("Meeting", meeting)
    meeting.check_permission("email")

    if meeting.status == "Planned":
        # Get attendee emails
        attendee_emails = [d.attendee for d in meeting.attendees if d.attendee]

        if attendee_emails:
            # Send email to attendees
            frappe.sendmail(
                recipients = attendee_emails,
                sender = frappe.session.user,
                subject = meeting.title,
                message = meeting.send_invitation_message,
                reference_doctype = meeting.doctype,
                reference_name = meeting.name,
                os_bulk = True
            )

            # Update meeting status
            meeting.status = "Invitation Sent"
            meeting.save()

            frappe.msgprint(_("Invitation Sent"))
        else:
            frappe.msgprint(_("No attendees found for this meeting"))
    else:
        frappe.msgprint(_("The meeting must be scheduled"))

@frappe .whitelist()
def get_meetings(start,end):
    if not frappe.has_permission("Meeting", "read"):
        raise frappe.PermissionError
#Return data from database of meeting
    return frappe.db.sql(
        """select timestamp(`date`, from_time)as start,
        timestamp(`date`, to_time)as end,
        name,
        title,
        status,
        0 as all_day 
        from `tabMeeting`
        where `date` between %(start)s and %(end)s""",{
        "start" : start,
        "end" : end
    },as_dict=True
    )

def meet_orientation_meeting(doc,method):
    """"Creating orientation meeting when new user is join"""
    meeting = frappe.get_doc({
        "doctype" : "Meeting",
        "title": "Orientationfor {0}".format(doc.first_name),
        "date" :add_days(nowdate(), 1),
        "from_time" : "9:00",
        "to_time" : "9:30",
        "attendees":[{
            "attendee" : doc.name
        }],
    })
    # Thw system manager have not the permission of meeting creation
    meeting.flags.ignore_permission(True)
    meeting.insert()