"""
Structure [Gear # { X: dir, Y: dir }]
  N { X: CTR, Y: CTR }
  1 { X: FWD, Y: FWD }
  2 { X: FWD, Y: RWD }
  3 { X: CTR, Y: FWD }
  4 { X: CTR, Y: RWD }
  5 { X: RWD, Y: FWD }
  6 { X: RWD, Y: RWD }
  7 [Err...]


Diagram of H-pattern layout and relative actuator positions

  1 3 5
  |_|_|  <--> Act X (across gate)
  | | |
  2 4 6

    ^
    |
    v
  Act Y

For Act X to move, Act Y must be in ctr position
"""


class LinearActuator:
    """
    This class defines the functionality of a linear actuator.
    A linear actuator can move both forwards and backwards from its rest state
    and is powered pneumatically.
    We will call the three possible positions: [FWD, CTR, RWD]
    """

    def __init__(self, name_):
        self.name = name_
        self.dir = "ctr"

    def move(self, dir_):
        valid_moves = [1, 0, -1]

        moves = {
            -1: "rwd",
            0: "ctr",
            1: "fwd"
        }

        if dir_ in valid_moves:
            old_dir = self.dir
            self.dir = moves[dir_]

            if old_dir != self.dir:
                print(f'{self.name} moved: {old_dir} >> {self.dir}')

        else:
            print(f'{dir_} is not a valid direction.')


def select_gear(gear_):
    target_gear = gear_

    gear_lut = {
        0: (0, 0),
        1: (1, 1),
        2: (1, -1),
        3: (0, 1),
        4: (0, -1),
        5: (-1, 1),
        6: (-1, -1)
    }

    print("------")
    print("Status: X: ", act_X.dir, ", Y: ", act_Y.dir)
    print(f'Target gear is {target_gear}')

    if target_gear in gear_lut:
        x, y = gear_lut[target_gear]
        act_Y.move(0)
        act_X.move(x)
        act_Y.move(y)
    else:
        print("invalid gear")


# Create the actuator instances
act_X = LinearActuator("act_X")
act_Y = LinearActuator("act_Y")

# Test Cases
select_gear(1)
select_gear(2)
select_gear(3)
select_gear(4)
select_gear(5)
select_gear(6)

select_gear(2)
select_gear(5)
select_gear(0)

select_gear(19)
