import readline
import cmd

DIGITS = {'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
          'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10}
TEENS = {'eleven': 11, 'twelve': 12, 'thirteen': 13, 'fourteen': 14, 'fifteen': 15,
         'sixteen': 16, 'seventeen': 17, 'eighteen': 18, 'nineteen': 19}
DECS = {'twenty': 20, 'thirty': 30, 'forty': 40, 'fifty': 50, 'sixty': 60, 'seventy': 70,
        'eighty': 80, 'ninety': 90}
ANY = DIGITS | TEENS | DECS


class numbername(cmd.Cmd):
    prompt = "cmd>> "

    def do_number(self, arg):
        """Translate two-digit number from english"""
        match arg.split():
            case [dec, digit]:
                if dec in DECS and digit in DIGITS:
                    print(DECS[dec] + DIGITS[digit])
            case [single]:
                if single in ANY:
                    print(ANY[single])

    def complete_number(self, text, line, begidx, endidx):
        words = (line[:endidx] + ".").split()
        DICT = []
        match len(words):
            case 2:
                DICT = ANY
            case 3:
                if words[1] in DECS:
                    DICT = DIGITS
        return [c for c in DICT if c.startswith(text)]

    def do_EOF(self, arg):
        return 1

class Calender(cmd.Cmd):
    prompt = "@@@ "

    def do_pryear(self, arg):
        '''     pryear(theyear)
                Print the calendar for an entire year as returned by formatyear().'''
        try:
            year = int(arg)
            calendar.TextCalendar().pryear(year)
        except Exception():
            print("Invalid parametr: pryear(?!)")
    
    def do_prmonth(self, arg):
        '''     prmonth(theyear, themonth)
                Print a month’s calendar as returned by formatmonth().'''
        try:
            year, month = map(int, arg.split())
            calendar.TextCalendar().prmonth(year, month)
        except Exception():
            print("Invalid parametr: pryear(?!)")

if __name__ == '__main__':
    numbername().cmdloop() 
