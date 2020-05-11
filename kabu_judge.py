import sys
import os
import csv
from math import ceil

FLUCTUATING = "波型"
DECREASING = "減少型"
SMALLSPIKE = "跳ね小型"
LARGESPIKE = "跳ね大型"

# カブ価関連情報を保持するクラス
class kabu_log:
    days = ('月曜AM','月曜PM','火曜AM','火曜PM','水曜AM','水曜PM','木曜AM','木曜PM','金曜AM','金曜PM','土曜AM','土曜PM')
    def __init__(self, data):
        for key in ('名前', '先週', '日曜', '月曜AM','月曜PM','火曜AM','火曜PM','水曜AM','水曜PM','木曜AM','木曜PM','金曜AM','金曜PM','土曜AM','土曜PM'):
            data.setdefault(key, '')

        self.username = data['名前']
        self.prices = dict()
        self.types = dict()

        if(data['日曜'] == ''):
            self.base = 0
        else:
            self.base = int(data['日曜'])

        for day in self.days:
            if(data[day] == ''):
                self.prices[day] = 0
            else:
                self.prices[day] = int(data[day])

        if(data['先週'] == FLUCTUATING):
            self.types = {FLUCTUATING : 0.20, DECREASING : 0.15, SMALLSPIKE : 0.35, LARGESPIKE : 0.30}
        elif(data['先週'] == DECREASING):
            self.types = {FLUCTUATING : 0.25, DECREASING : 0.05, SMALLSPIKE : 0.25, LARGESPIKE : 0.45}
        elif(data['先週'] == SMALLSPIKE):
            self.types = {FLUCTUATING : 0.45, DECREASING : 0.15, SMALLSPIKE : 0.15, LARGESPIKE : 0.25}
        elif(data['先週'] == LARGESPIKE):
            self.types = {FLUCTUATING : 0.50, DECREASING : 0.20, SMALLSPIKE : 0.25, LARGESPIKE : 0.05}
        else:
            self.types = {FLUCTUATING : 0.25, DECREASING : 0.25, SMALLSPIKE : 0.25, LARGESPIKE : 0.25}

                                      
# kabu_logに変動型判定機能を追加したクラス
class kabu_judge(kabu_log):
    def __init__(self,data):
        super().__init__(data)
        self.fluctuating = []
        self.decreasing = []
        self.smallspike = []
        self.peakpoints_s = []
        self.largespike = []
        self.peakpoints_l = []        
        if(self.base == 0):
            self.base4gen = [90,110]
        else:
            self.base4gen = [self.base, self.base]

    # 波型の許容範囲を生成
    def gen_fluctuating(self):
        # 各フェーズの長さで場合分けして全パターン生成
        for hiPhaseLen1 in range(7):
            hiPhaseLen2and3 = 7 - hiPhaseLen1
            for hiPhaseLen2 in range(1, hiPhaseLen2and3+1):
                for decPhaseLen1 in (2,3):
                    prices_rng = [[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0]]
                    # 増加フェーズ
                    for i in range(hiPhaseLen1):     
                        prices_rng[i] = [ceil(self.base4gen[0] * 0.9), ceil(self.base4gen[1] * 1.4)]
                    # 減少フェーズ
                    price0 = [self.base4gen[0] * 0.6, self.base4gen[1] * 0.8]
                    for i in range(hiPhaseLen1, hiPhaseLen1+decPhaseLen1):        
                        prices_rng[i] = [ceil(price0[0]), ceil(price0[1])]
                        if(self.prices[self.days[i]] == 0):    
                            price0 = [price0[0] + self.base4gen[1]*(-0.1), price0[1] + self.base4gen[0]*(-0.04)]
                        else:
                            price0 = [self.prices[self.days[i]] + self.base4gen[1]*(-0.1), self.prices[self.days[i]] + self.base4gen[0]*(-0.04)]        
                    # 増加フェーズ
                    for i in range(hiPhaseLen1+decPhaseLen1, hiPhaseLen1+decPhaseLen1+hiPhaseLen2):
                        prices_rng[i] = [ceil(self.base4gen[0] * 0.9), ceil(self.base4gen[1] * 1.4)] 
                    # 減少フェーズ
                    price0 = [self.base4gen[0] * 0.6, self.base4gen[1] * 0.8]
                    for i in range(hiPhaseLen1+decPhaseLen1+hiPhaseLen2, hiPhaseLen1+hiPhaseLen2+5):       
                        prices_rng[i] = [ceil(price0[0]), ceil(price0[1])]  
                        if(self.prices[self.days[i]] == 0):    
                            price0 = [price0[0] + self.base4gen[1]*(-0.1), price0[1] + self.base4gen[0]*(-0.04)]
                        else:
                            price0 = [self.prices[self.days[i]] + self.base4gen[1]*(-0.1), self.prices[self.days[i]] + self.base4gen[0]*(-0.04)]        
                    # 増加フェーズ
                    for i in range(hiPhaseLen1+hiPhaseLen2+5, 12):
                        prices_rng[i] = [ceil(self.base4gen[0] * 0.9), ceil(self.base4gen[1] * 1.4)]   
                    self.fluctuating.append(prices_rng)

    # 減少型の許容範囲を生成
    def gen_decreasing(self):
        prices_rng = [[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0]]
        price0 = [self.base4gen[0] * 0.85, self.base4gen[1] * 0.9]
        for i in range(12):        
            prices_rng[i] = [ceil(price0[0]), ceil(price0[1])]
            if(self.prices[self.days[i]] == 0):    
                price0 = [price0[0] + self.base4gen[1]*(-0.05), price0[1] + self.base4gen[0]*(-0.03)]
            else:
                price0 = [self.prices[self.days[i]] + self.base4gen[1]*(-0.05), self.prices[self.days[i]] + self.base4gen[0]*(-0.03)]                     
        self.decreasing.append(prices_rng)

    # 跳ね小型の許容範囲を生成
    def gen_smallspike(self):
        for decPhaseLen1 in range(8):
            prices_rng = [[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0]]
            # 減少フェーズ
            price0 = [self.base4gen[0] * 0.4, self.base4gen[1] * 0.9]
            for i in range(decPhaseLen1):     
                prices_rng[i] = [ceil(price0[0]), ceil(price0[1])]
                if(self.prices[self.days[i]] == 0):    
                    price0 = [price0[0] + self.base4gen[1]*(-0.05), price0[1] + self.base4gen[0]*(-0.03)]
                else:
                    price0 = [self.prices[self.days[i]] + self.base4gen[1]*(-0.05), self.prices[self.days[i]] + self.base4gen[0]*(-0.03)]
            # 跳ね12
            for i in range(decPhaseLen1, decPhaseLen1+2):
                prices_rng[i] = [ceil(self.base4gen[0] * 0.9), ceil(self.base4gen[1] * 1.4)] 
            # 跳ね3
            if(self.prices[self.days[decPhaseLen1+3]] == 0):
                prices_rng[decPhaseLen1+2] = [ceil(self.base4gen[0] * 1.4), ceil(self.base4gen[1] * 2.0)]
            else:
                prices_rng[decPhaseLen1+2] = [ceil(self.base4gen[0] * 1.4), self.prices[self.days[decPhaseLen1+3]]]
            # 跳ね4
            prices_rng[decPhaseLen1+3] = [ceil(self.base4gen[0] * 1.4), ceil(self.base4gen[1] * 2.0)]
            # 跳ね5
            if(self.prices[self.days[decPhaseLen1+3]] == 0):
                prices_rng[decPhaseLen1+4] = [ceil(self.base4gen[0] * 1.4), ceil(self.base4gen[1] * 2.0)]
            else:
                prices_rng[decPhaseLen1+4] = [ceil(self.base4gen[0] * 1.4), self.prices[self.days[decPhaseLen1+3]]]
            # 減少フェーズ
            price0 = [self.base4gen[0] * 0.4, self.base4gen[1] * 0.9]
            for i in range(decPhaseLen1+5, 12):     
                prices_rng[i] = [ceil(price0[0]), ceil(price0[1])]
                if(self.prices[self.days[i]] == 0):    
                    price0 = [price0[0] + self.base4gen[1]*(-0.05), price0[1] + self.base4gen[0]*(-0.03)]
                else:
                    price0 = [self.prices[self.days[i]] + self.base4gen[1]*(-0.05), self.prices[self.days[i]] + self.base4gen[0]*(-0.03)]
            self.smallspike.append(prices_rng)
            self.peakpoints_s.append(self.days[decPhaseLen1+3])
    
    # 跳ね大型の許容範囲を生成
    def gen_largespike(self):
        for decPhaseLen1 in range(1,8):
            prices_rng = [[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0]]
            # 減少フェーズ
            price0 = [self.base4gen[0] * 0.85, self.base4gen[1] * 0.9]
            for i in range(decPhaseLen1):     
                prices_rng[i] = [ceil(price0[0]), ceil(price0[1])]
                if(self.prices[self.days[i]] == 0):    
                    price0 = [price0[0] + self.base4gen[1]*(-0.05), price0[1] + self.base4gen[0]*(-0.03)]
                else:
                    price0 = [self.prices[self.days[i]] + self.base4gen[1]*(-0.05), self.prices[self.days[i]] + self.base4gen[0]*(-0.03)]
            # 跳ね1
            prices_rng[decPhaseLen1] = [ceil(self.base4gen[0] * 0.9), ceil(self.base4gen[1] * 1.4)]
            # 跳ね2
            prices_rng[decPhaseLen1+1] = [ceil(self.base4gen[0] * 1.4), ceil(self.base4gen[1] * 2.0)]
            # 跳ね3
            prices_rng[decPhaseLen1+2] = [ceil(self.base4gen[0] * 2.0), ceil(self.base4gen[1] * 6.0)]
            # 跳ね4
            prices_rng[decPhaseLen1+3] = [ceil(self.base4gen[0] * 1.4), ceil(self.base4gen[1] * 2.0)]
            # 跳ね5
            prices_rng[decPhaseLen1+4] = [ceil(self.base4gen[0] * 0.9), ceil(self.base4gen[1] * 1.4)]
            # 減少フェーズ
            for i in range(decPhaseLen1+5, 12):     
                prices_rng[i] = [ceil(self.base4gen[0] * 0.4), ceil(self.base4gen[1] * 0.9)]
            self.largespike.append(prices_rng)   
            self.peakpoints_l.append(self.days[decPhaseLen1+2])    

    # 各変動型においてあり得るパターン数を返す関数、跳ねる型の場合ピーク位置も返す（パターン数１の場合だけ有効）
    def judge_each(self, pattern, peakpoints=None):
        FUDGE_FACTOR = 5
        pattern_num = 0
        fudge = True # Trueかつpattern_num>0ならFUDGE_FACTORでギリギリあり得ると判定されたことを意味する
        peakpoint = None
        for i, prices_rng in enumerate(pattern):
            for price_rng, price in zip(prices_rng, self.prices.values()):
                if(price == 0):
                    pass
                elif((price < price_rng[0]-FUDGE_FACTOR) or (price > price_rng[1]+FUDGE_FACTOR)):              
                    break
            else:
                pattern_num += 1
                if(peakpoints is not None): peakpoint = peakpoints[i]

            if(fudge):
                for price_rng, price in zip(prices_rng, self.prices.values()):
                    if(price == 0):
                        pass
                    elif((price < price_rng[0]) or (price > price_rng[1])):              
                        break
                else:
                    fudge = False

        if(peakpoints is None): return pattern_num, fudge
        else: return pattern_num, fudge, peakpoint 

    def judge(self):
        # fluctuating_num0 = 56
        # decreasing_num0 = 1
        # smallspike_num0 = 8
        # largespike_num0 = 7  
        fudge = dict()
        
        self.gen_fluctuating()
        fluctuating_num, fudge[FLUCTUATING] = self.judge_each(self.fluctuating)
        if(fluctuating_num == 0): self.types[FLUCTUATING] = 0

        self.gen_decreasing()
        decreasing_num, fudge[DECREASING] = self.judge_each(self.decreasing)
        if(decreasing_num == 0): self.types[DECREASING] = 0

        self.gen_smallspike()
        smallspike_num, fudge[SMALLSPIKE], peakpoint_s = self.judge_each(self.smallspike, self.peakpoints_s)
        if(smallspike_num == 0): self.types[SMALLSPIKE] = 0

        self.gen_largespike()
        largespike_num, fudge[LARGESPIKE], peakpoint_l = self.judge_each(self.largespike, self.peakpoints_l)
        if(largespike_num == 0): self.types[LARGESPIKE] = 0

        if(self.types[LARGESPIKE] > 0):
            if(largespike_num == 1 and self.prices[peakpoint_l] > 0): peak = self.prices[peakpoint_l]
            else: peak = ceil(self.base4gen[1] * 6.0)
        elif(self.types[SMALLSPIKE] > 0):
            if(smallspike_num == 1 and self.prices[peakpoint_s] > 0): peak = self.prices[peakpoint_s]
            else: peak = ceil(self.base4gen[1] * 2.0)            
        elif(self.types[FLUCTUATING] > 0):
            peak = ceil(self.base4gen[1] * 1.4)
        elif(self.types[DECREASING] > 0):
            if(self.prices[self.days[0]] == 0): peak = ceil(self.base4gen[1] * 0.9)
            else: peak = self.prices[self.days[0]]            

        for kabutype in (FLUCTUATING, DECREASING, SMALLSPIKE, LARGESPIKE):
            if(self.types[kabutype] <= 0): self.types.pop(kabutype)

        result = ''
        if(self.types):    
            result += self.username + " : "
            for key in self.types: 
                if(fudge[key]):
                    result += "(" + key + ")" + ", "
                else:
                    result += key + ", "
            result += "限界値=" + str(peak)
        else:
            result = self.username + " : 判定不能"
        
        return result

if __name__ == '__main__':
    args = sys.argv
    if(len(args) != 2):
        print("エラー：引数が正しくありません。以下のような形式で実行してください。", file=sys.stderr)
        print("$ python " + os.path.basename(__file__) + " hoge.csv")     
        sys.exit(1)  
    if(os.path.splitext(args[1])[1] != ".csv"):
        print("エラー：引数が正しくありません。csvファイルを指定してください。", file=sys.stderr)
        sys.exit(1)

    log = list()
    with open(args[1], 'r') as f:
        for row in csv.DictReader(f):
            log.append(kabu_judge(row))

    for user in log:
        print(user.judge())

