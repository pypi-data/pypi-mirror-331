#
from .. import evalz,xf,Base

class VarEval(evalz.Eval):
    def init(self, key, stype = 'list'):
        self.key = key
        self.stype = stype
    def call(self, obj):
        args, maps = obj.args, obj.maps
        if self.stype=='list':
            return args[self.key]
        return maps[self.key]
class VarBuild(evalz.Build):
    def init(self, stype="list"):
        super().init()
        self.stype = stype
    def call(self, data):
        return VarEval(data['data'][0], self.stype)
lb = VarBuild('list')
db = VarBuild('dict')
evalBuilder = evalz.EvalBuilder.Make().set(["l","list","args"], lb).set(['d','dict','maps'], db)
