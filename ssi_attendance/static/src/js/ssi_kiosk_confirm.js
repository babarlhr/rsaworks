odoo.define('hr_attendance.kiosk_confirm', function (require) {
"use strict";

var AbstractAction = require('web.AbstractAction');
var core = require('web.core');
var QWeb = core.qweb;


var KioskConfirm = AbstractAction.extend({
    events: {
        "click .o_hr_attendance_back_button": function () { this.do_action(this.next_action, {clear_breadcrumbs: true}); },
        "click .o_hr_attendance_sign_in_out_icon": _.debounce(function () {
            var self = this;
            this._rpc({
                    model: 'hr.employee',
                    method: 'attendance_manual',
                    args: [[this.employee_id], this.next_action],
                })
                .then(function(result) {
                    if (result.action) {
                        self.do_action(result.action);
                    } else if (result.warning) {
                        self.do_warn(result.warning);
                    }
                });
        }, 200, true),
        'click .o_hr_attendance_pin_pad_button_0': function() { this.$('.o_hr_attendance_PINbox').val(this.$('.o_hr_attendance_PINbox').val() + 0); },
        'click .o_hr_attendance_pin_pad_button_1': function() { this.$('.o_hr_attendance_PINbox').val(this.$('.o_hr_attendance_PINbox').val() + 1); },
        'click .o_hr_attendance_pin_pad_button_2': function() { this.$('.o_hr_attendance_PINbox').val(this.$('.o_hr_attendance_PINbox').val() + 2); },
        'click .o_hr_attendance_pin_pad_button_3': function() { this.$('.o_hr_attendance_PINbox').val(this.$('.o_hr_attendance_PINbox').val() + 3); },
        'click .o_hr_attendance_pin_pad_button_4': function() { this.$('.o_hr_attendance_PINbox').val(this.$('.o_hr_attendance_PINbox').val() + 4); },
        'click .o_hr_attendance_pin_pad_button_5': function() { this.$('.o_hr_attendance_PINbox').val(this.$('.o_hr_attendance_PINbox').val() + 5); },
        'click .o_hr_attendance_pin_pad_button_6': function() { this.$('.o_hr_attendance_PINbox').val(this.$('.o_hr_attendance_PINbox').val() + 6); },
        'click .o_hr_attendance_pin_pad_button_7': function() { this.$('.o_hr_attendance_PINbox').val(this.$('.o_hr_attendance_PINbox').val() + 7); },
        'click .o_hr_attendance_pin_pad_button_8': function() { this.$('.o_hr_attendance_PINbox').val(this.$('.o_hr_attendance_PINbox').val() + 8); },
        'click .o_hr_attendance_pin_pad_button_9': function() { this.$('.o_hr_attendance_PINbox').val(this.$('.o_hr_attendance_PINbox').val() + 9); },
        'click .o_hr_attendance_pin_pad_button_C': function() { this.$('.o_hr_attendance_PINbox').val(''); },
        'click .o_hr_attendance_pin_pad_button_ok': _.debounce(function() {
            var self = this;
            this.$('.o_hr_attendance_pin_pad_button_ok').attr("disabled", "disabled");
            var end_job = 'True';
            this._rpc({
                    model: 'hr.employee',
                    method: 'attendance_manual',
                    args: [
                      [this.employee_id],
                      this.next_action,
                      this.$('.o_hr_attendance_PINbox').val(),
                      this.$('#job-select').val(),
                      this.$('#wo-select').val(),
                      end_job
                    ]
                })
                .then(function(result) {
                    if (result.action) {
                        self.do_action(result.action);
                    } else if (result.warning) {
                        self.do_warn(result.warning);
                        self.$('.o_hr_attendance_PINbox').val('');
                        setTimeout( function() { self.$('.o_hr_attendance_pin_pad_button_ok').removeAttr("disabled"); }, 500);
                    }
                });
        }, 200, true),
        'click .o_hr_attendance_switch_button': _.debounce(function() {
            var self = this;
            this.$('.o_hr_attendance_pin_pad_switch_button').attr("disabled", "disabled");
            var end_job = 'False';
            this._rpc({
                    model: 'hr.employee',
                    method: 'attendance_manual',
                    args: [
                      [this.employee_id],
                      this.next_action,
                      this.$('.o_hr_attendance_PINbox').val(),
                      this.$('#job-select').val(),
                      this.$('#wo-select').val(),
                      this.$('.close-wo:checked').val(),
                      end_job
                    ]
                })
                .then(function(result) {
                    if (result.action) {
                        self.do_action(result.action);
                    } else if (result.warning) {
                        self.do_warn(result.warning);
                        self.$('.o_hr_attendance_PINbox').val('');
                        setTimeout( function() { self.$('.o_hr_attendance_pin_pad_button_ok').removeAttr("disabled"); }, 500);
                    }
                });
        }, 200, true),
        'click .o_hr_attendance_clock_out_button': _.debounce(function() {
            var self = this;
            this.$('.o_hr_attendance_pin_pad_check_out_button').attr("disabled", "disabled");
            var end_job = 'True';
            this._rpc({
                    model: 'hr.employee',
                    method: 'attendance_manual',
                    args: [
                      [this.employee_id],
                      this.next_action,
                      this.$('.o_hr_attendance_PINbox').val(),
                      this.$('#job-select').val(),
                      this.$('#wo-select').val(),
                      this.$('.close-wo:checked').val(),
                      end_job
                    ]
                })
                .then(function(result) {
                    if (result.action) {
                        self.do_action(result.action);
                    } else if (result.warning) {
                        self.do_warn(result.warning);
                        self.$('.o_hr_attendance_PINbox').val('');
                        setTimeout( function() { self.$('.o_hr_attendance_pin_pad_button_ok').removeAttr("disabled"); }, 500);
                    }
                });
        }, 200, true),
        "click .o_hr_attendance_split_button": _.debounce(function () {
            var self = this;
            this._rpc({
                    model: 'hr.employee',
                    method: 'attendance_check_pin',
                    args: [
                        [this.employee_id], 
                        this.next_action, 
                        this.$('.o_hr_attendance_PINbox').val(),
                    ],
                })
                .then(function(result) {
                    if (result.warning) {
                        self.do_warn(result.warning);
                        self.$('.o_hr_attendance_PINbox').val('');
                        setTimeout( function() { self.$('.o_hr_attendance_pin_pad_button_ok').removeAttr("disabled"); }, 500);
                    } else {
                        self.$el.html(QWeb.render("ssi_attendance.HrAttendanceSplitTime", {widget: self}));
                    }
                });
        }, 200, true),
        "click .o_hr_attendance_split_out_button": _.debounce(function () {
            var self = this;
            var end_job = 'True';
            var job = [];
            var wo = [];
            var close = [];
            
            this.$('.job-select').each(function(i) {
                if (this.value) {job[i] = this.value};
            });
            this.$('.wo-select').each(function(i) {
                if (this.value) {wo[i] = this.value};
            });
            this.$('.close-wo').each(function(i) {
                if (this.value) {close[i] = this.value};
            });
            this._rpc({
                    model: 'hr.employee',
                    method: 'attendance_split_time',
                    args: [
                        [this.employee_id], 
                        this.next_action,
                        job,
                        wo,
                        close,
                        end_job
                    ],
                })
                .then(function(result) {
                    if (result.action) {
                        self.do_action(result.action);
                    } else if (result.warning) {
                        self.do_warn(result.warning);
                    }
                });
        }, 200, true),
        "click .o_hr_attendance_split_switch_button": _.debounce(function () {
            var self = this;
            var end_job = 'False';
            var job = [];
            var wo = [];
            var close = [];
            
            this.$('.job-select').each(function(i) {
                if (this.value) {job[i] = this.value};
            });
            this.$('.wo-select').each(function(i) {
                if (this.value) {wo[i] = this.value};
            });
            this.$('.close-wo').each(function(i) {
                if (this.value) {close[i] = this.value};
            });
            this._rpc({
                    model: 'hr.employee',
                    method: 'attendance_split_time',
                    args: [
                        [this.employee_id], 
                        this.next_action,
                        job,
                        wo,
                        close,
                        end_job
                    ],
                })
                .then(function(result) {
                    if (result.action) {
                        self.do_action(result.action);
                    } else if (result.warning) {
                        self.do_warn(result.warning);
                    }
                });
        }, 200, true),
        'change .job-select': function(event) {
          var job_id = event.target.value;
          console.log(event.target.dataset.wo);
          var wo_dropdown = this.$(event.target.dataset.wo);
          var html = '';
          this._rpc({
            model: 'mrp.workorder',
            method: 'search_read',
            args: [[['ssi_job_id.id', '=', job_id], ['hide_in_kiosk', '=', false]]]
          }).then(function(results) {
            console.log(results);
            if (results) {
              html = html + `<option value="" class="text-success font-weight-bold">Select a Workorder</option>`;
              results.forEach(function(w) {
                  if (w.state == 'done') {
                    html = html + `<option value="${w.id}" class="text-success font-weight-bold">${w.display_name}</option>`;
                  } else{
                    html = html + `<option value="${w.id}">${w.display_name}</option>`;
                  }
              });
            }
            if (html === '') {
              html = "<option value=''>No Work Order available for this Job</option>";
            }
            wo_dropdown.html(html);
          });
        },

    },

    init: function (parent, action) {
        this._super.apply(this, arguments);
        this.next_action = 'hr_attendance.hr_attendance_action_kiosk_mode';
        this.employee_id = action.employee_id;
        this.employee_name = action.employee_name;
        this.employee_state = action.employee_state;
        //         CUSTOM
        this.jobs = [];
        this.wos = [];
    },

    start: function () {
        var self = this;
        this._rpc({
            model: 'ssi_jobs',
            method: 'search_read',
            args: [[['hide_in_kiosk', '=', false]], [], [], [], 'name']
        }).then(function(result) {
            var ele = {id:'', display_name:'Please Select a Job'};
            self.jobs = result;
            self.jobs.unshift(ele);
            console.log(self)
            self.getSession().user_has_group('hr_attendance.group_hr_attendance_use_pin').then(function(has_group){
                self.use_pin = has_group;
                self.$el.html(QWeb.render("ssi_attendance.HrAttendanceKioskConfirm", {widget: self}));
                self.start_clock();
            });
        });
        return self._super.apply(this, arguments);
    },

    start_clock: function () {
        this.clock_start = setInterval(function() {this.$(".o_hr_attendance_clock").text(new Date().toLocaleTimeString(navigator.language, {hour: '2-digit', minute:'2-digit', second:'2-digit'}));}, 500);
        // First clock refresh before interval to avoid delay
        this.$(".o_hr_attendance_clock").show().text(new Date().toLocaleTimeString(navigator.language, {hour: '2-digit', minute:'2-digit', second:'2-digit'}));
    },

    destroy: function () {
        clearInterval(this.clock_start);
        this._super.apply(this, arguments);
    },
});

core.action_registry.add('hr_attendance_kiosk_confirm', KioskConfirm);

return KioskConfirm;

});
