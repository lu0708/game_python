import tkinter as tk
import random
import os

# 配料清单及颜色替代
ingredients = {
    "bun_top": "brown",
    "lettuce": "green",
    "tomato": "red",
    "cheese": "yellow",
    "patty": "darkred",
    "bun_bottom": "brown"
}
non_bun_ingredients = ["lettuce", "tomato", "cheese", "patty"]

# 客户名单
customers = ["Alice", "Bob", "Charlie", "David"]

# 游戏计时长度（秒）根据难度
DIFFICULTY_SETTINGS = {
    'easy': {'time': 60, 'min_ingredients': 2, 'max_ingredients': 3},
    'medium': {'time': 60, 'min_ingredients': 3, 'max_ingredients': 4},
    'hard': {'time': 60, 'min_ingredients': 4, 'max_ingredients': 5}
}

# 随机产生订单
def generate_order(difficulty_settings):
    order = ["bun_bottom"]
    num_non_bun_ingredients = random.randint(difficulty_settings['min_ingredients'], difficulty_settings['max_ingredients'])
    for _ in range(num_non_bun_ingredients):
        order.append(random.choice(non_bun_ingredients))
    order.append("bun_top")
    return order

# 读取历史最高分
def load_highscore():
    if os.path.exists("highscore.txt"):
        with open("highscore.txt", "r") as file:
            return int(file.read())
    return 0

# 保存历史最高分
def save_highscore(score):
    with open("highscore.txt", "w") as file:
        file.write(str(score))

class BurgerGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Burger Game")

        self.score = 0
        self.high_score = load_highscore()
        self.level = 1  # 游戏级别（默认为1）
        self.difficulty_level = 'easy'
        self.difficulty_settings = DIFFICULTY_SETTINGS[self.difficulty_level]
        self.time_left = self.difficulty_settings['time']
        self.running = True

        self.customer_name = random.choice(customers)
        self.order = generate_order(self.difficulty_settings)
        self.current_burger = []

        self.create_ui()

        self.update_timer()

    def create_ui(self):
        # 设置顶部分隔框架
        self.top_frame = tk.Frame(self.root)
        self.top_frame.pack(side=tk.TOP, fill=tk.X)

        self.customer_label = tk.Label(self.top_frame, text="Customer: " + self.customer_name)
        self.customer_label.pack()

        self.order_label = tk.Label(self.top_frame, text="Order: " + ", ".join(self.order))
        self.order_label.pack()

        self.burger_label = tk.Label(self.top_frame, text="Your Burger: ")
        self.burger_label.pack()

        self.score_label = tk.Label(self.top_frame, text="Score: 0")
        self.score_label.pack()

        self.timer_label = tk.Label(self.top_frame, text="Time left: " + str(self.time_left))
        self.timer_label.pack()

        self.level_label = tk.Label(self.top_frame, text="Level: " + str(self.level))
        self.level_label.pack()

        # 历史最高分标签设置在右上角
        self.high_score_label = tk.Label(self.root, text="High Score: " + str(self.high_score))
        self.high_score_label.pack(anchor='ne', padx=10, pady=10)  # 显示在右上角

        self.buttons_frame = tk.Frame(self.root)
        self.buttons_frame.pack()

        for ingredient, color in ingredients.items():
            button = tk.Button(self.buttons_frame, text=ingredient, bg=color, command=lambda ing=ingredient: self.add_ingredient(ing))
            button.pack(side=tk.LEFT)

        self.check_button = tk.Button(self.root, text="Check Burger", command=self.check_burger)
        self.check_button.pack()

        # 设置画布用来显示掉落的方块
        self.canvas = tk.Canvas(self.root, width=800, height=600)
        self.canvas.pack()

        self.burger_blocks = []
        self.current_height = 500

    def add_ingredient(self, ingredient):
        if self.running:
            self.current_burger.append(ingredient)
            self.burger_label.config(text="Your Burger: " + ", ".join(self.current_burger))
            self.check_burger_incrementally()
            self.drop_block(ingredient)

    def drop_block(self, ingredient):
        color = ingredients[ingredient]
        start_y = 0
        end_y = self.current_height
        block_id = self.canvas.create_rectangle(375, start_y, 425, start_y + 25, fill=color)
        self.animate_block(block_id, start_y, end_y)
        self.current_height -= 25  # 更新堆叠高度

    def animate_block(self, block_id, start_y, end_y, step=2):
        if start_y < end_y:
            self.canvas.move(block_id, 0, step)
            self.root.after(100, self.animate_block, block_id, start_y + step, end_y)
        else:
            self.burger_blocks.append(block_id)

    def check_burger_incrementally(self):
        if self.running:
            for i in range(len(self.current_burger)):
                if self.current_burger[i] != self.order[i]:
                    self.game_over()
                    return

    def check_burger(self):
        if self.running:
            if self.current_burger == self.order:
                self.score += 10
                self.score_label.config(text="Score: " + str(self.score))
                self.update_high_score()
                self.increase_difficulty()  # 提升难度
                self.reset_game()
            else:
                self.game_over()

    def reset_game(self):
        self.customer_name = random.choice(customers)
        self.order = generate_order(self.difficulty_settings)
        self.current_burger = []
        self.current_height = 500

        self.customer_label.config(text="Customer: " + self.customer_name)
        self.order_label.config(text="Order: " + ", ".join(self.order))
        self.burger_label.config(text="Your Burger: ")

        for block_id in self.burger_blocks:
            self.canvas.delete(block_id)
        self.burger_blocks = []

    def update_timer(self):
        if self.running:
            self.time_left -= 1
            self.timer_label.config(text="Time left: " + str(self.time_left))
            if self.time_left <= 0:
                self.game_over()
            else:
                self.root.after(1000, self.update_timer)

    def increase_difficulty(self):
        # 提升等待时间等级
        self.level += 1
        self.level_label.config(text="Level: " + str(self.level))

        # 根据久期提升难度
        if self.level <= 5:
            self.difficulty_level = 'easy'
        elif self.level <= 10:
            self.difficulty_level = 'medium'
        else:
            self.difficulty_level = 'hard'
            
        self.difficulty_settings = DIFFICULTY_SETTINGS[self.difficulty_level]

    def update_high_score(self):
        if self.score > self.high_score:
            self.high_score = self.score
            save_highscore(self.high_score)
            self.high_score_label.config(text="High Score: " + str(self.high_score))

    def game_over(self):
        self.running = False
        self.reset_to_first_level()

    def reset_to_first_level(self):
        self.level = 1
        self.difficulty_level = 'easy'
        self.difficulty_settings = DIFFICULTY_SETTINGS[self.difficulty_level]
        self.running = True
        self.score = 0
        self.time_left = self.difficulty_settings['time']
        self.score_label.config(text="Score: 0")
        self.level_label.config(text="Level: 1")
        self.reset_game()
        self.update_timer()

if __name__ == "__main__":
    root = tk.Tk()
    app = BurgerGame(root)
    root.mainloop()
