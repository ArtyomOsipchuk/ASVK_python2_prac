import cmd
import calendar

class Calendar(cmd.Cmd):
    prompt = "@@@ "
    Month = {m.name: m.value for m in calendar.Month}

    def do_pryear(self, arg):
        '''     pryear(theyear)
                Print the calendar for an entire year as returned by formatyear().'''
        try:
            year = int(arg)
            calendar.TextCalendar().pryear(year)
        except Exception:
            print("Invalid parametr: pryear(?!)")

    def do_prmonth(self, arg):
        '''     prmonth(theyear, themonth)
                Print a month’s calendar as returned by formatmonth().'''
        try:
            year, month = arg.split()
            calendar.TextCalendar().prmonth(int(year), self.Month[month])
        except Exception as e:
            print("Invalid parametr: prmonth(?!)", e)
    
    def do_EOF(self, arg):
        return 1

    def complete_prmonth(self, text, line, begidx, endidx):
        words = (line[:endidx] + ".").split()
        DICT = []
        if len(words) == 3:
            DICT = ["JANUARY", "FEBRUARY", "MARCH",
                   "APRIL", "MAY", "JUNE", "JULY",
                   "AUGUST", "SEPTEMBER", "OCTOBER", "NOVEMBER", "DECEMBER"]
        return [c for c in DICT if c.startswith(text)]

if __name__ == '__main__':
    Calendar().cmdloop()

