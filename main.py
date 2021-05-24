import re, random, math
import typer # FROM MATHAR PROJ.

class Robot():

    MIN_RANDOM = 1
    MAX_RANDOM = 50
    MAX_RECURSION = 1000
    SHUFFLE = True

    def prepare_samples(self, queue):
        res = []
        for q in queue:
            res.extend(list(self.generate(q))) 
            #del used keys.
            del q['raw']
            del q['rules']
            del q['face']
            del q['count']

        if self.SHUFFLE:
            random.shuffle(res)

        return res

    def generate(self, head):
        #init
        raw = head['raw']
        rules = head['rules']
        face = head['face']
        count = head['count']
        vars = self.extract_vars(raw)
        res = set()
        c = 0
        while len(res)<count and c<self.MAX_RECURSION:
            c += 1
            values = self.gen_random(vars)

            sample = self.replace_vars(face, values)

            if all([self.evaluate(self.replace_vars(i, values)) for i in rules]): # assure all rules are true.
                res.add(sample)

        if not len(res)==count:
            print(f'<ERROR>: only {len(res)} is made out of {count}.')

        return res

    def extract_vars(self, txt):
        return re.findall(r'[a-z]', txt)

    def gen_random(self, vars):
        return {v: random.randint(self.MIN_RANDOM, self.MAX_RANDOM) for v in vars}

    def replace_vars(self, txt, trans):
        for i, j in trans.items():
            txt = txt.replace(i, str(j))
        return txt

    def evaluate(self, exp):
        return eval(exp)


class Drawer(typer.Typer):

    POS  = 0
    SIZE = (2480, 3508)
    HMARGIN = 50
    

    def __init__(self, data):
        super().__init__()
        self.debug = False
        self.font_size = 100
        self.VMARGIN = int(self.font_size*.8)
        self.init()

        self.paper = self.frame(self.SIZE, color='white')
        self.data = data
        self.PILS = self.gen_PILs() 
         
        self.init_lengths()
        
    def init_lengths(self): 
        self._25px = 25
        self._50px = int(self.font_size * 0.6) #linear.
        self._100px = 100
        self._200px = 200
        self.paper_hmargin = self._200px+self._100px #paper half margin(right margin).
        self.paper_margin = self.paper_hmargin*2
        self.five_divs = (self.SIZE[0]-self.paper_margin)//5
        self.four_divs = (self.SIZE[0]-self.paper_margin)//4
        self.three_divs = (self.SIZE[0]-self.paper_margin)//3
        self.two_divs = (self.SIZE[0]-self.paper_margin)//2
        self.one_div = (self.SIZE[0]-self.paper_margin)
        self.jumpsDict ={ 
            5:self.five_divs, 
            4:self.four_divs, 
            3:self.three_divs, 
            2:self.two_divs, 
            1:self.one_div
        }

    def gen_PILs(self):
        if len(self.data)==0:
            return [self.ERROR]
        return [self.robot(i) for i in self.data]

    def row_capacity(self):
        max_width = self.get_max_width()['w']
        return (self.SIZE[0]-(self.HMARGIN*len(self.data)-2))//max_width

    def get_max_width(self):
        return max(self.PILS, key=lambda x:x['w'])

    def get_max_height(self):
        return max(self.PILS, key=lambda x:x['h'])

    def simple_grid(self, col_count:int=5):
        col_count = col_count if col_count<=len(self.PILS) else len(self.PILS) # this escaped a bug.
        while col_count>=1:
            rows = [self.PILS[i:i+col_count] for i in range(0, len(self.PILS), col_count)] 
            rows_widths = [map(lambda x: x['w'], row) for row in rows]
            jump = self.jumpsDict[col_count]
            if all(map(lambda c: (c['w']+self.NUMB['w']+10)<=jump, self.PILS)) or col_count==1: 
                return {
                    'col_count': col_count,
                    'row_count': math.ceil(len(self.PILS)/col_count),
                    'col_widths': [jump,]*col_count}
            else:
                col_count -= 1

    def draw_probs(self):
        steps = self.simple_grid()
        max_height = self.get_max_height()
        col_width = steps['col_widths'][0]
        #init
        w, y = 0, 200
        counter = 0
        for row in range(steps['row_count']):
            for col in range(steps['col_count']):
                try:
                    PIL = self.PILS[counter]
                except:
                    break

                x = self.SIZE[0]-col_width+(col_width-PIL['w'])-w-self.paper_hmargin-self.NUMB['w']

                self.paper.paste(PIL['p'], (x, y+max_height['u']-PIL['u']), mask=PIL['p']) 

                # numbering
                NUMB = self.robot(f'n({counter+1})')

                nx = self.SIZE[0]-col_width+(col_width-self.NUMB['w'])-w-self.paper_hmargin
                ny = max(self.NUMB['u'], PIL['u'])+max(self.NUMB['l'], PIL['l']) + self.VMARGIN
                self.paper.paste(NUMB['p'], (nx, y+max_height['u']-self.NUMB['u']), mask=NUMB['p'])

                #col calcs
                w+= col_width
                counter += 1
            #row calcs
            y += max(max_height['u'], PIL['u'])+max(max_height['l'], PIL['l']) + self.VMARGIN
            w = 0

        self.paper.show()

if __name__=='__main__':
    from pprint import pprint
    data = [
    			#{'raw':str, 'count':str, 'face':str, 'rules':list}
                {'raw': 'a/b', 'count': 20, 'face': 'f(a&b)=h(3)', 'rules': ['(a/b)==int(a/b)', 'a!=b', 'b!=1']},
                {'raw': 'a/(b**0.5)', 'count': 16, 'face': 'f(a&r(b))=h(3)', 'rules': ['a/(b**0.5)==int(a/(b**0.5))', 'b!=1']},
    ]

    obj = Robot().prepare_samples(data)

    obj2 = Drawer(data=obj).draw_probs()

    pprint(obj2)




