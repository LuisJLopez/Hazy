import numpy as np

from typing import List
from plotly import graph_objects as go


class WorldObject:

    draw_mode = "markers"

    def __init__(self, obj_id: str, initx: int, inity: int):
        self.obj_id: str = obj_id
        self.posx: int = initx
        self.posy: int = inity
        self.collided: bool = False

    def move(self, step_x: int, step_y: int):
        self.posx += step_x
        self.posy += step_y

    def update_state(self):
        raise NotImplementedError()


class Bubble(WorldObject):
    def __init__(self, obj_id: str, initx: int, inity: int):
        super().__init__(obj_id, initx, inity)

    def update_state(self):
        direction = np.random.choice(["left", "right", "up", "down", "stay"])
        if direction == "left":
            self.move(-1, 0)
        elif direction == "right":
            self.move(1, 0)
        elif direction == "up":
            self.move(0, 1)
        elif direction == "down":
            self.move(0, -1)

    def draw(self) -> go.Scatter:
        return go.Scatter(
            x=[self.posx], y=[self.posy], mode=self.draw_mode, marker={"color": "green"}
        )

    def draw_collision(self) -> go.Scatter:
        return go.Scatter(
            x=[self.posx],
            y=[self.posy],
            mode=self.draw_mode,
            marker={"color": "red"},
        )

    def set_collision(self, bubbles: list):
        # when a collision of bubbles is found
        # set collided attribute as True
        for bubble in bubbles:
            if (
                self.posx == bubble.posx
                and self.posy == bubble.posy
                and self.obj_id != bubble.obj_id
            ):
                setattr(self, "collided", True)


class Rock(WorldObject):
    def move(self):
        pass

    def update_state(self):
        pass

    def draw(self) -> go.Scatter:
        return go.Scatter(
            x=[self.posx],
            y=[self.posy],
            mode=self.draw_mode,
            marker={"color": "yellow"},
        )

    def draw_collision(self):
        pass

    def set_collision(self):
        pass


class WorldGrid:
    def __init__(self, width: int, height: int, w_objects: List[WorldObject]):
        self.width = width
        self.height = height
        self.w_objects = w_objects

    def update_state(self):
        # only updating state for bubbles that haven't yet collided
        # quickly skipping interation when obj doesn't need state update
        for w_object in self.w_objects:
            if isinstance(w_object, Rock) or w_object.collided:
                continue
            elif isinstance(w_object, Bubble) or not w_object.collided:
                w_object.update_state()

    def check_for_collisions(self):
        bubbles = [obj for obj in self.w_objects if isinstance(obj, Bubble)]

        for bubble in bubbles:
            bubble.set_collision(bubbles)

    def fetch_object_drawings(self) -> List[Bubble]:
        draw_objects = []

        # drawing depending on obj and collision status
        # skipping loop straight away if instance of Rock
        for w_object in self.w_objects:
            if isinstance(w_object, Rock):
                continue
            elif isinstance(w_object, Bubble) and w_object.collided:
                draw_objects.append(w_object.draw_collision())
            elif isinstance(w_object, Bubble) and not w_object.collided:
                draw_objects.append(w_object.draw())

        return draw_objects

    def get_frame(self, frame_number: int) -> go.Frame:
        return go.Frame(
            data=self.fetch_object_drawings(),
            layout=go.Layout(title_text=f"Simulation frame {frame_number}"),
        )

    def create_simulation(self, steps: int):
        frames = []

        for i in range(steps):
            self.update_state()
            self.check_for_collisions()
            frames.append(self.get_frame(i))

        fig = go.Figure(
            data=[w_obj.draw() for w_obj in self.w_objects],
            layout=go.Layout(
                xaxis=dict(range=[0, self.width], autorange=False),
                yaxis=dict(range=[0, self.height], autorange=False),
                title="Simulation",
                updatemenus=[
                    dict(
                        type="buttons",
                        buttons=[dict(label="Play", method="animate", args=[None])],
                    )
                ],
            ),
            frames=frames,
        )
        fig.show()


def simulate():
    bubbles: List[Bubble] = [
        Bubble(f"bubble_{i}_{j}", i, j)
        for i in range(5, 15, 2)
        for j in range(5, 15, 2)
    ]

    rocks: List[Rock] = [
        Rock("rock_2_2", 2, 2),
        Rock("rock_18_18", 18, 18),
        Rock("rock_3_15", 3, 15),
    ]
    world = WorldGrid(20, 20, bubbles + rocks)
    world.create_simulation(steps=50)


simulate()
