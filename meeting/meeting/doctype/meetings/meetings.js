// Copyright (c) 2024, Shivam and contributors
// For license information, please see license.txt

frappe.ui.form.on("Meeting Attendee", {
    attendee: function(frm, cdt, cdn) {
        var attendee = frappe.model.get_doc(cdt, cdn);
        if (attendee.attendee) {
            frappe.call({
                method: "meeting.meeting.doctype.meetings.meetings.get_full_name",
                args: {
                    attendee: attendee.attendee
                },
                callback: function(r) {
                    if (r.exc) {
                        frappe.msgprint(r.exc);
                    } else {
                        frappe.model.set_value(cdt, cdn, "full_name", r.message);
                    }
                }
            });
        } else {
            frappe.model.set_value(cdt, cdn, "full_name", null);
        }
    }
});

frappe.ui.form.on("Meeting", {
    send_emails: function(frm) {
        if (frm.doc.status === "Planned") {
            frappe.call({
                method: "meeting.api.send_invitation_emails",
                args: {
                    meeting: frm.doc.name
                },
                callback: function(r) {
                    if (r.exc) {
                        frappe.msgprint(r.exc);
                    } else {
                        frappe.msgprint("Invitation emails sent successfully");
                    }
                }
            });
        } else {
            frappe.msgprint("Meeting status must be 'Planned' to send invitation emails");
        }
    }
});