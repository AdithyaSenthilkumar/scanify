frappe.ui.form.on('Scheme Request', {
    refresh: function(frm) {
        // Set status indicator
        if (frm.doc.approval_status) {
            let color = {
                'Approved': 'green',
                'Rejected': 'red',
                'Rerouted': 'orange',
                'Pending': 'blue'
            }[frm.doc.approval_status] || 'gray';
            
            frm.dashboard.set_headline_alert(
                `Status: ${frm.doc.approval_status}`, 
                color
            );
        }
        
        // Manager action buttons
        if (frm.doc.docstatus === 0 && 
            frm.doc.approval_status === 'Pending' && 
            !frm.is_new() &&
            (frappe.user.has_role('Sales Manager') || frappe.user.has_role('System Manager'))) {
            
            frm.add_custom_button(__('Approve'), function() {
                approve_scheme(frm);
            }, __('Actions')).css({'background-color': '#28a745', 'color': 'white'});
            
            frm.add_custom_button(__('Reject'), function() {
                reject_scheme(frm);
            }, __('Actions')).css({'background-color': '#dc3545', 'color': 'white'});
            
            frm.add_custom_button(__('Reroute'), function() {
                reroute_scheme(frm);
            }, __('Actions')).css({'background-color': '#fd7e14', 'color': 'white'});
        }
        
        // View attachments button
        if (frm.doc.proof_attachment_1 || frm.doc.proof_attachment_2 || 
            frm.doc.proof_attachment_3 || frm.doc.proof_attachment_4) {
            frm.add_custom_button(__('View Documents'), function() {
                show_all_attachments(frm);
            });
        }
    },
    
    search_doctor: function(frm) {
        if (frm.doc.search_doctor && frm.doc.search_doctor.length >= 2) {
            show_doctor_search_dialog(frm);
        }
    },
    
    doctor_code: function(frm) {
        if (frm.doc.doctor_code) {
            frappe.db.get_value('Doctor Master', frm.doc.doctor_code, 
                ['doctor_name', 'place', 'city_pool', 'team', 'region', 'specialization', 'hospital_clinic'], 
                (r) => {
                    if (r) {
                        frm.set_value('doctor_name', r.doctor_name);
                        frm.set_value('doctor_place', r.place);
                        frm.set_value('city_pool', r.city_pool);
                        frm.set_value('team', r.team);
                        frm.set_value('region', r.region);
                        frm.set_value('specialization', r.specialization);
                        frm.set_value('hospital_clinic', r.hospital_clinic);
                    }
            });
        }
    }
});

frappe.ui.form.on('Scheme Request Item', {
    quantity: function(frm, cdt, cdn) {
        calculate_item_value(frm, cdt, cdn);
    },
    
    special_rate: function(frm, cdt, cdn) {
        calculate_item_value(frm, cdt, cdn);
    },
    
    product_code: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.product_code) {
            frappe.db.get_value('Product Master', row.product_code, 
                ['product_name', 'pack', 'pts'], (r) => {
                    frappe.model.set_value(cdt, cdn, 'product_name', r.product_name);
                    frappe.model.set_value(cdt, cdn, 'pack', r.pack);
                    frappe.model.set_value(cdt, cdn, 'product_rate', r.pts);
            });
        }
    }
});

function show_doctor_search_dialog(frm) {
    let d = new frappe.ui.Dialog({
        title: 'Search Doctor',
        fields: [
            {
                fieldname: 'search_results',
                fieldtype: 'HTML'
            }
        ],
        primary_action_label: 'Close',
        primary_action: function() {
            d.hide();
        }
    });
    
    frappe.call({
        method: 'scanify.api.search_doctors',
        args: { search_term: frm.doc.search_doctor },
        callback: function(r) {
            if (r.message && r.message.length > 0) {
                let html = `
                    <div style="max-height: 400px; overflow-y: auto;">
                        <table class="table table-bordered">
                            <thead>
                                <tr>
                                    <th>Doctor</th>
                                    <th>Place</th>
                                    <th>Specialization</th>
                                    <th>Action</th>
                                </tr>
                            </thead>
                            <tbody>
                `;
                
                r.message.forEach(function(doctor) {
                    html += `
                        <tr>
                            <td><strong>${doctor.doctor_name}</strong><br><small>${doctor.doctor_code}</small></td>
                            <td>${doctor.place || '-'}</td>
                            <td>${doctor.specialization || 'General'}</td>
                            <td>
                                <button class="btn btn-xs btn-primary select-doctor" data-code="${doctor.name}">
                                    Select
                                </button>
                            </td>
                        </tr>
                    `;
                });
                
                html += '</tbody></table></div>';
                d.fields_dict.search_results.$wrapper.html(html);
                
                d.fields_dict.search_results.$wrapper.find('.select-doctor').on('click', function() {
                    let code = $(this).data('code');
                    frm.set_value('doctor_code', code);
                    d.hide();
                });
            } else {
                d.fields_dict.search_results.$wrapper.html(
                    '<div class="alert alert-warning">No doctors found</div>'
                );
            }
        }
    });
    
    d.show();
}

function calculate_item_value(frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    let rate = row.special_rate ? flt(row.special_rate) : flt(row.product_rate);
    let value = flt(row.quantity) * rate;
    frappe.model.set_value(cdt, cdn, 'product_value', value);
    calculate_total(frm);
}

function calculate_total(frm) {
    let total = 0;
    (frm.doc.items || []).forEach(item => {
        total += flt(item.product_value);
    });
    frm.set_value('total_scheme_value', total);
}

function approve_scheme(frm) {
    frappe.prompt([
        {
            fieldname: 'comments',
            fieldtype: 'Small Text',
            label: 'Approval Comments',
            reqd: 1
        }
    ], (values) => {
        frappe.call({
            method: 'scanify.api.approve_scheme_request',
            args: {
                doc_name: frm.doc.name,
                comments: values.comments
            },
            callback: function(r) {
                if (r.message) {
                    frm.reload_doc();
                    frappe.show_alert({
                        message: 'Scheme approved successfully',
                        indicator: 'green'
                    }, 5);
                }
            }
        });
    }, __('Approve Scheme'), __('Approve'));
}

function reject_scheme(frm) {
    frappe.prompt([
        {
            fieldname: 'comments',
            fieldtype: 'Small Text',
            label: 'Rejection Reason',
            reqd: 1
        }
    ], (values) => {
        frappe.call({
            method: 'scanify.api.reject_scheme_request',
            args: {
                doc_name: frm.doc.name,
                comments: values.comments
            },
            callback: function(r) {
                if (r.message) {
                    frm.reload_doc();
                    frappe.show_alert({
                        message: 'Scheme rejected',
                        indicator: 'red'
                    }, 5);
                }
            }
        });
    }, __('Reject Scheme'), __('Reject'));
}

function reroute_scheme(frm) {
    frappe.prompt([
        {
            fieldname: 'comments',
            fieldtype: 'Small Text',
            label: 'Reroute Reason',
            reqd: 1
        }
    ], (values) => {
        frappe.call({
            method: 'scanify.api.reroute_scheme_request',
            args: {
                doc_name: frm.doc.name,
                comments: values.comments
            },
            callback: function(r) {
                if (r.message) {
                    frm.reload_doc();
                    frappe.show_alert({
                        message: 'Scheme rerouted for revision',
                        indicator: 'orange'
                    }, 5);
                }
            }
        });
    }, __('Reroute Scheme'), __('Reroute'));
}

function show_all_attachments(frm) {
    let attachments = [];
    [1, 2, 3, 4].forEach(i => {
        let att = frm.doc[`proof_attachment_${i}`];
        if (att) attachments.push({ num: i, url: att });
    });
    
    let html = '<div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px;">';
    attachments.forEach(att => {
        let isImage = att.url.match(/\\.(jpg|jpeg|png|gif)$/i);
        html += `
            <div style="border: 2px solid #ddd; border-radius: 8px; padding: 10px; text-align: center;">
                <h5>Document ${att.num}</h5>
                ${isImage ? 
                    `<img src="${att.url}" style="width: 100%; cursor: pointer;" 
                        onclick="window.open('${att.url}', '_blank')"/>` :
                    `<p><i class="fa fa-file"></i> ${att.url.split('/').pop()}</p>`
                }
                <button class="btn btn-sm btn-default" style="margin-top: 8px;" 
                    onclick="window.open('${att.url}', '_blank')">
                    <i class="fa fa-external-link"></i> View/Download
                </button>
            </div>
        `;
    });
    html += '</div>';
    
    frappe.msgprint({
        title: __('Attached Documents'),
        message: html,
        wide: true
    });
}