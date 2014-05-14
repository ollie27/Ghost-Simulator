__author__ = 'Martin'

from gslib import primitives


################################################################################
### fear harvested functions
################################################################################
def red_square(obj):  # get ooga booga'd
    def func(harvester):
        obj.fear = 0
        obj.fainted = True

        sprite = primitives.RectPrimitive(width=10, height=10, color=(120, 0, 0))
        obj.flair['fear_harvested'] = (sprite, (-5, obj.dimensions[1] + 5))
    func.__name__ = 'red_square'
    return func
