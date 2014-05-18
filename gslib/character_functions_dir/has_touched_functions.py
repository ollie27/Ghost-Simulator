from __future__ import absolute_import, division, print_function

__author__ = 'Martin'

################################################################################
### touch functions
### These happen when a character has touched or untouched
################################################################################
def touched_flip_state(obj):
    def func(toucher):  # need to accept toucher, even if this function don't need it!
        obj.state_index = str((int(obj.state_index) + 1) % len(obj.states))
        # print obj.state_index
    func.__name__ = 'touched_flip_state'
    return func
