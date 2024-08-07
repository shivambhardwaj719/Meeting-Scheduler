# Copyright (c) 2024, Shivam and contributors
# For license information, please see license.txt
from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _
from typing import List
from frappe.model.naming import get_default_naming_series
from frappe.model.mapper import get_mapped_doc
from frappe.utils import now
# from frappe.model import attach_validation

class Meetings(Document):
    def validate(self):
        # Fetch all user documents at once for efficiency
        users = {user.email: user for user in frappe.db.get_all("User", fields=["email", "first_name", "middle_name", "last_name"])}
        
        seen_attendees = set()
        for attendee in self.attendees:
            if attendee.attendee in seen_attendees:
                frappe.throw(_("Attendee {0} is already added to this meeting.").format(attendee.attendee))
            seen_attendees.add(attendee.attendee)
            
            if not attendee.full_name:
                attendee.full_name = self.get_full_name(attendee.attendee, users)
    
    def validate(self):
        # ... (rest of the code remains the same)

        # Check for overlapping meetings
        self.check_for_overlapping_meetings()

    def check_for_overlapping_meetings(self):
        for attendee in self.attendees:
            overlapping_meetings = frappe.get_all("Meetings", filters={
                'attendees': ['like', f'%{attendee.attendee}%'],
                'docstatus': 1,
                'from_time': ['<', self.to_time],
                'to_time': ['>', self.from_time]
            })

            if overlapping_meetings:
                for meeting in overlapping_meetings:
                    meeting_doc = frappe.get_doc("Meetings", meeting.title)
                    for meeting_attendee in meeting_doc.attendees:
                        if meeting_attendee.attendee == attendee.attendee:
                            # Check if the attendee is already in a meeting
                            if meeting_doc.from_time <= self.from_time < meeting_doc.to_time:
                                frappe.throw(_("User {0} is already in a meeting: {1}").format(attendee.attendee, meeting_doc.title))
    # def check_for_overlapping_meeting(self):
    #     for attendee in self.attendees:
    #          overlapping_meetings = frappe.get_all("Meeting", filters={
    #               'attendees': ['like', f'%{attendee.attendee}%'],
    #               'from_time': ['<', self.to_time],
    #               'to_time': ['>', self.from_time]
    #     })
        
    #     if overlapping_meetings:
    #         for meeting in overlapping_meetings:
    #             # Use correct placeholders for string formatting
    #             frappe.msgprint(_("User {0} is in another meeting titled {1}".format(attendee.attendee, meeting.title)))
    
    
#     def validate_meeting_overlap(doc, method):
#          # Get the user's current meetings
#          user_meetings = frappe.db.sql("""
#                                         SELECT 
#                                        name,
#                                        from_time,
#                                        to_time 
#                                        FROM 
#                                        `tabMeeting` 
#                                        WHERE 
#                                        status = 'Scheduled' 
#                                        AND docstatus = 1 
#                                        AND from_time <= %s 
#                                        AND to_time >= %s 
#                                        AND attendees LIKE %s
#                                        """, (now(), now(), "%" + doc.attendees + "%"), as_dict=True)
#          for meeting in user_meetings:
#             if meeting.from_time <= doc.from_time < meeting.to_time:
#                  frappe.throw("User is already in a meeting: " + meeting.title)

# # Attach the validation to the Meeting doctype
#     attach_validation("Meeting", validate_meeting_overlap)

@frappe.whitelist()
def get_full_name(attendee: str) -> str:
	"""Fetches the full name of a user given their email."""
	user = frappe.get_doc("User",attendee)
	frappe.msgprint(str(user.first_name))
	if user:
		return " ".join(filter(None, [user.first_name, user.middle_name, user.last_name]))
	else:
		# Handle the case when the user is not found
		frappe.msgprint(_("User {0} not found.").format(attendee), alert=True)
		return ""
