odoo.define('hr_attendance.greeting_message_custom', function(require) {
  'use strict';

  console.log('SSI CUSTOM JAVASCRIPT 2');

  // var AbstractAction = require('web.AbstractAction');
  var GreatingMessageOld = require('hr_attendance.greeting_message');
  var core = require('web.core');

  var _t = core._t;

  var GreetingMessage = GreatingMessageOld.extend({
    // template: 'ssi_attendance.HrAttendanceGreetingMessageCustom',
    // xmlDependencies: ['/ssi_attendance/static/src/xml/attendance.xml'],

    events: {
      'click .o_hr_attendance_button_dismiss': function() {
        this.do_action(this.next_action, { clear_breadcrumbs: true });
      },
      'click .o_hr_attendance_button_switch_task': function() {
        this.custom_start_clock();
      }
    },

    init: function(parent, action) {
      var self = this;
      this._super.apply(this, arguments);
      this.activeBarcode = true;

      // if no correct action given (due to an erroneous back or refresh from the browser), we set the dismiss button to return
      // to the (likely) appropriate menu, according to the user access rights
      if (!action.attendance) {
        this.activeBarcode = false;
        this.getSession()
          .user_has_group('hr_attendance.group_hr_attendance_user')
          .then(function(has_group) {
            if (has_group) {
              self.next_action =
                'hr_attendance.hr_attendance_action_kiosk_mode';
            } else {
              self.next_action =
                'hr_attendance.hr_attendance_action_my_attendances';
            }
          });
        return;
      }

      this.next_action =
        action.next_action ||
        'hr_attendance.hr_attendance_action_my_attendances';
      // no listening to barcode scans if we aren't coming from the kiosk mode (and thus not going back to it with next_action)
      if (
        this.next_action != 'hr_attendance.hr_attendance_action_kiosk_mode' &&
        this.next_action.tag != 'hr_attendance_kiosk_mode'
      ) {
        this.activeBarcode = false;
      }

      this.attendance = action.attendance;

      // We receive the check in/out times in UTC
      // This widget only deals with display, which should be in browser's TimeZone
      this.attendance.check_in =
        this.attendance.check_in &&
        moment.utc(this.attendance.check_in).local();
      this.attendance.check_out =
        this.attendance.check_out &&
        moment.utc(this.attendance.check_out).local();
      this.previous_attendance_change_date =
        action.previous_attendance_change_date &&
        moment.utc(action.previous_attendance_change_date).local();

      //         CUSTOM
      this.jobs = action.jobs;
      this.wos = action.wos;
      // this.lcs = action.lcs;

      // check in/out times displayed in the greeting message template.
      this.format_time = 'HH:mm:ss';
      this.attendance.check_in_time =
        this.attendance.check_in &&
        this.attendance.check_in.format(this.format_time);
      this.attendance.check_out_time =
        this.attendance.check_out &&
        this.attendance.check_out.format(this.format_time);
      this.employee_name = action.employee_name;
      this.attendanceBarcode = action.barcode;
    },

    start: function() {
      if (this.attendance) {
        this.attendance.check_out
          ? this.farewell_message()
          : this.welcome_message();
      }
      if (this.activeBarcode) {
        core.bus.on('barcode_scanned', this, this._onBarcodeScanned);
      }
    },

    custom_start_clock: function() {
      var self = this;
      console.log(this.next_action);
    },

    welcome_message: function() {
      var self = this;
      var now = this.attendance.check_in.clone();
      this.return_to_main_menu = setTimeout(function() {
        self.do_action(self.next_action, { clear_breadcrumbs: true });
      }, 5000);

      if (now.hours() < 5) {
        this.$('.o_hr_attendance_message_message').append(_t('Good night'));
      } else if (now.hours() < 12) {
        if (now.hours() < 8 && Math.random() < 0.3) {
          if (Math.random() < 0.75) {
            this.$('.o_hr_attendance_message_message').append(
              _t('The early bird catches the worm')
            );
          } else {
            this.$('.o_hr_attendance_message_message').append(
              _t('First come, first served')
            );
          }
        } else {
          this.$('.o_hr_attendance_message_message').append(_t('Good morning'));
        }
      } else if (now.hours() < 17) {
        this.$('.o_hr_attendance_message_message').append(_t('Good afternoon'));
      } else if (now.hours() < 23) {
        this.$('.o_hr_attendance_message_message').append(_t('Good evening'));
      } else {
        this.$('.o_hr_attendance_message_message').append(_t('Good night'));
      }
      if (this.previous_attendance_change_date) {
        var last_check_out_date = this.previous_attendance_change_date.clone();
        if (now - last_check_out_date > 24 * 7 * 60 * 60 * 1000) {
          this.$('.o_hr_attendance_random_message').html(
            _t("Glad to have you back, it's been a while!")
          );
        } else {
          if (Math.random() < 0.02) {
            this.$('.o_hr_attendance_random_message').html(
              _t('If a job is worth doing, it is worth doing well!')
            );
          }
        }
      }
    },

    farewell_message: function() {
      var self = this;
      var now = this.attendance.check_out.clone();

      //STOP REFRESH CUSTOM
      //         this.return_to_main_menu = setTimeout( function() { self.do_action(self.next_action, {clear_breadcrumbs: true}); }, 5000);

      if (this.previous_attendance_change_date) {
        var last_check_in_date = this.previous_attendance_change_date.clone();
        if (now - last_check_in_date > 1000 * 60 * 60 * 12) {
          this.$('.o_hr_attendance_warning_message')
            .show()
            .append(
              _t(
                "<b>Warning! Last check in was over 12 hours ago.</b><br/>If this isn't right, please contact Human Resource staff"
              )
            );
          clearTimeout(this.return_to_main_menu);
          this.activeBarcode = false;
        } else if (now - last_check_in_date > 1000 * 60 * 60 * 8) {
          this.$('.o_hr_attendance_random_message').html(
            _t("Another good day's work! See you soon!")
          );
        }
      }

      if (now.hours() < 12) {
        this.$('.o_hr_attendance_message_message').append(
          _t('Have a good day!')
        );
      } else if (now.hours() < 14) {
        this.$('.o_hr_attendance_message_message').append(
          _t('Have a nice lunch!')
        );
        if (Math.random() < 0.05) {
          this.$('.o_hr_attendance_random_message').html(
            _t(
              'Eat breakfast as a king, lunch as a merchant and supper as a beggar'
            )
          );
        } else if (Math.random() < 0.06) {
          this.$('.o_hr_attendance_random_message').html(
            _t('An apple a day keeps the doctor away')
          );
        }
      } else if (now.hours() < 17) {
        this.$('.o_hr_attendance_message_message').append(
          _t('Have a good afternoon')
        );
      } else {
        if (now.hours() < 18 && Math.random() < 0.2) {
          this.$('.o_hr_attendance_message_message').append(
            _t(
              'Early to bed and early to rise, makes a man healthy, wealthy and wise'
            )
          );
        } else {
          this.$('.o_hr_attendance_message_message').append(
            _t('Have a good evening')
          );
        }
      }
    },

    _onBarcodeScanned: function(barcode) {
      var self = this;
      if (this.attendanceBarcode !== barcode) {
        if (this.return_to_main_menu) {
          // in case of multiple scans in the greeting message view, delete the timer, a new one will be created.
          clearTimeout(this.return_to_main_menu);
        }
        core.bus.off('barcode_scanned', this, this._onBarcodeScanned);
        this._rpc({
          model: 'hr.employee',
          method: 'attendance_scan',
          args: [barcode]
        }).then(
          function(result) {
            if (result.action) {
              self.do_action(result.action);
            } else if (result.warning) {
              self.do_warn(result.warning);
              setTimeout(function() {
                self.do_action(self.next_action, { clear_breadcrumbs: true });
              }, 5000);
            }
          },
          function() {
            setTimeout(function() {
              self.do_action(self.next_action, { clear_breadcrumbs: true });
            }, 5000);
          }
        );
      }
    },

    destroy: function() {
      core.bus.off('barcode_scanned', this, this._onBarcodeScanned);
      clearTimeout(this.return_to_main_menu);
      this._super.apply(this, arguments);
    }
  });

  core.action_registry.add('hr_attendance_greeting_message', GreetingMessage);

  return GreetingMessage;
});

//! HERE HERE HERE SEPARATION

odoo.define('hr_attendance.kiosk_confirm_custom', function(require) {
  'use strict';

  var KioskConfirm = require('hr_attendance.kiosk_confirm');
  var core = require('web.core');
  var QWeb = core.qweb;

  KioskConfirm.include({
    template: 'ssi_attendance.HrAttendanceKioskConfirmCustom',
    xmlDependencies: ['/ssi_attendance/static/src/xml/attendance.xml'],
    events: {
      'click .o_hr_attendance_back_button': function() {
        this.do_action(this.next_action, { clear_breadcrumbs: true });
      },
      'click .o_hr_attendance_sign_in_out_icon': function() {
        var self = this;
        this.$('.o_hr_attendance_sign_in_out_icon').attr(
          'disabled',
          'disabled'
        );
        this._rpc({
          model: 'hr.employee',
          method: 'attendance_manual',
          args: [[this.employee_id], this.next_action]
        }).then(function(result) {
          if (result.action) {
            self.do_action(result.action);
          } else if (result.warning) {
            self.do_warn(result.warning);
            self.$('.o_hr_attendance_sign_in_out_icon').removeAttr('disabled');
          }
        });
      },
      'click .o_hr_attendance_pin_pad_button_0': function() {
        this.$('.o_hr_attendance_PINbox').val(
          this.$('.o_hr_attendance_PINbox').val() + 0
        );
      },
      'click .o_hr_attendance_pin_pad_button_1': function() {
        this.$('.o_hr_attendance_PINbox').val(
          this.$('.o_hr_attendance_PINbox').val() + 1
        );
      },
      'click .o_hr_attendance_pin_pad_button_2': function() {
        this.$('.o_hr_attendance_PINbox').val(
          this.$('.o_hr_attendance_PINbox').val() + 2
        );
      },
      'click .o_hr_attendance_pin_pad_button_3': function() {
        this.$('.o_hr_attendance_PINbox').val(
          this.$('.o_hr_attendance_PINbox').val() + 3
        );
      },
      'click .o_hr_attendance_pin_pad_button_4': function() {
        this.$('.o_hr_attendance_PINbox').val(
          this.$('.o_hr_attendance_PINbox').val() + 4
        );
      },
      'click .o_hr_attendance_pin_pad_button_5': function() {
        this.$('.o_hr_attendance_PINbox').val(
          this.$('.o_hr_attendance_PINbox').val() + 5
        );
      },
      'click .o_hr_attendance_pin_pad_button_6': function() {
        this.$('.o_hr_attendance_PINbox').val(
          this.$('.o_hr_attendance_PINbox').val() + 6
        );
      },
      'click .o_hr_attendance_pin_pad_button_7': function() {
        this.$('.o_hr_attendance_PINbox').val(
          this.$('.o_hr_attendance_PINbox').val() + 7
        );
      },
      'click .o_hr_attendance_pin_pad_button_8': function() {
        this.$('.o_hr_attendance_PINbox').val(
          this.$('.o_hr_attendance_PINbox').val() + 8
        );
      },
      'click .o_hr_attendance_pin_pad_button_9': function() {
        this.$('.o_hr_attendance_PINbox').val(
          this.$('.o_hr_attendance_PINbox').val() + 9
        );
      },

      'change #job-select': function() {
        var job_id = this.$('#job-select').val();
        var wo_dropdown = this.$('#wo-select-js');
        var html = '';
        this._rpc({
          model: 'mrp.workorder',
          method: 'search_read',
          args: [[['ssi_job_id.id', '=', job_id]]]
        }).then(function(results) {
          console.log(results);
          if (results) {
            results.forEach(function(w) {
              html =
                html + `<option value="${w.id}">${w.display_name}</option>`;
            });
          }
          if (html === '') {
            html =
              "<option value=''>No Work Order available for this JOb</option>";
          }
          wo_dropdown.html(html);
        });
      },

      'click .o_hr_attendance_pin_pad_button_C': function() {
        this.$('.o_hr_attendance_PINbox').val('');
      },
      'click .o_hr_attendance_pin_pad_button_ok': function() {
        var self = this;
        this.$('.o_hr_attendance_pin_pad_button_ok').attr(
          'disabled',
          'disabled'
        );

        var end = 'True';
        if (this.$("input[name='end-job']:checked").val() !== undefined) {
          end = this.$("input[name='end-job']:checked")
            .val()
            .toString();
        }
        console.log('CHECK VALUES', end);
        this._rpc({
          model: 'hr.employee',
          method: 'attendance_manual',
          args: [
            [this.employee_id],
            this.next_action,
            this.$('.o_hr_attendance_PINbox').val(),
            this.$('#job-select').val(),
            this.$('#wo-select-js').val(),
            // this.$('#lc-select').val(),
            end
          ]
        }).then(function(result) {
          if (result.action) {
            self.do_action(result.action);
          } else if (result.warning) {
            self.do_warn(result.warning);
            self.$('.o_hr_attendance_PINbox').val('');
            setTimeout(function() {
              self
                .$('.o_hr_attendance_pin_pad_button_ok')
                .removeAttr('disabled');
            }, 500);
          }
        });
      }
    },

    init: function(parent, action) {
      this._super.apply(this, arguments);
      this.next_action = 'hr_attendance.hr_attendance_action_kiosk_mode';
      this.employee_id = action.employee_id;
      this.employee_name = action.employee_name;
      this.employee_state = action.employee_state;
      //         CUSTOM
      this.jobs = [];
      this.wos = [];
      // this.lcs = [];
    },
    start: function() {
      var self = this;
      async function renderWithDropdowns() {
        try {
          self.jobs = await self._rpc({
            model: 'ssi_jobs',
            method: 'search_read',
            args: [[]]
          });

          self.wos = await self._rpc({
            model: 'mrp.workorder',
            method: 'search_read',
            args: [[['ssi_job_id', '=', self.jobs[0].id]]]
          });

          // var i;
          // for (i = 0; i < self.jobs.length; i++) {
          //   var wo = await self._rpc({
          //     model: 'mrp.workorder',
          //     method: 'search_read',
          //     args: [[['ssi_job_id', '=', self.jobs[i].id]]]
          //   });
          //   self.wos.push(wo);
          // }
          // self.lcs = await self._rpc({
          //   model: 'x_labor.codes',
          //   method: 'search_read',
          //   args: [[]]
          // });

          console.log('JOBZ', self.jobs);
          // console.log('WOZ', self.wos);
          // console.log('LCZ', self.lcs);

          self
            .getSession()
            .user_has_group('hr_attendance.group_hr_attendance_use_pin')
            .then(function(has_group) {
              self.use_pin = has_group;
              // setTimeout(function() {
              self.$el.html(
                QWeb.render('ssi_attendance.HrAttendanceKioskConfirmCustom', {
                  widget: self
                })
              );
              // }, 100);
              self.start_clock();
            });
        } catch (error) {
          console.log(error);
        }
      }
      renderWithDropdowns();
      return self._super.apply(this, arguments);
    }
  });

  core.action_registry.add('hr_attendance_kiosk_confirm', KioskConfirm);

  return KioskConfirm;
});

// odoo.define('hr_attendance.my_attendances', function (require) {
// "use strict";

// var AbstractAction = require('web.AbstractAction');
// var core = require('web.core');

// var QWeb = core.qweb;
// var _t = core._t;

// var MyAttendances = AbstractAction.extend({
//     events: {
//         "click .o_hr_attendance_sign_in_out_icon": _.debounce(function() {
//             this.update_attendance();
//         }, 200, true),
//     },

//     start: function () {
//         var self = this;

//         var def = this._rpc({
//                 model: 'hr.employee',
//                 method: 'search_read',
//                 args: [[['user_id', '=', this.getSession().uid]], ['attendance_state', 'name']],
//             })
//             .then(function (res) {
//                 self.employee = res.length && res[0];
//                 self.$el.html(QWeb.render("HrAttendanceMyMainMenu", {widget: self}));
//             });

//         return $.when(def, this._super.apply(this, arguments));
//     },

//     update_attendance: function () {
//         var self = this;
//         this._rpc({
//                 model: 'hr.employee',
//                 method: 'attendance_manual',
//                 args: [[self.employee.id], 'hr_attendance.hr_attendance_action_my_attendances'],
//             })
//             .then(function(result) {
//                 if (result.action) {
//                     self.do_action(result.action);
//                 } else if (result.warning) {
//                     self.do_warn(result.warning);
//                 }
//             });
//     },
// });

// core.action_registry.add('hr_attendance_my_attendances', MyAttendances);

// return MyAttendances;

// });
