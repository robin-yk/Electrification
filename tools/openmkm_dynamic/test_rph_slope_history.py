"""Regression check for unnecessary solver resets during isothermal holds."""
from rph_candidate_flow_pilot import update_slope
class Reactor:
    slope=0.
class Network:
    resets=0
    def reinitialize(self):self.resets+=1
r=Reactor();n=Network()
for slope in [10.,10.,0.,0.,0.,-10.,-10.]:
    update_slope(r,n,slope)
assert n.resets==3, n.resets
assert r.slope==-10.
print('PASS: reset only at a change in prescribed slope')
