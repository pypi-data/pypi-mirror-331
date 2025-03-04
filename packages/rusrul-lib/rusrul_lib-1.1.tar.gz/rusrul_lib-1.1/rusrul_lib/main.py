# Russian Roulette Lib
# by LEYN1092
import random

class revolver:
    def __init__(self, ammo: int = 1, clipSize: int = 6):
        # Antibug
        if clipSize <= 0: clipSize = 6
        if ammo <= 0: ammo = 0
        if ammo > clipSize: ammo = clipSize
        # Params
        self.clipSize: int = clipSize
        self.clip: list = [1 for _ in range(ammo)] + [0 for _ in range(clipSize - ammo)]
        random.shuffle(self.clip)
        # Customization
        self.strAmmo: str = "#"
        self.strEmpty: str = "."
        self.reprVisualise: bool = True
        self.allowStrPattern: bool = False
        self.onShoot = "..."
    def __str__(self):
        if self.reprVisualise:
            if not self.allowStrPattern:
                return "".join([self.strAmmo if i else self.strEmpty for i in self.clip])
            else:
                return "".join(self.clip)
        else:
            return f"revolver({self.ammoCount()}, {self.clipSize}) = {self.clip}"
    def spin(self, spinPower: int = 0):
        if spinPower == 0:
            spinPower = random.randrange(self.clipSize)
        else:
            spinPower = spinPower % self.clipSize
        self.clip = self.clip[spinPower:6] + self.clip[0:spinPower]
    def shoot(self):
        temp = self.clip[0]
        if temp:
            self.clip[0] = 0 if not self.allowStrPattern else "0"
        self.spin(1)
        if temp and not self.allowStrPattern:
            exec(self.onShoot)
        return temp
    def load(self, pattern: str = ""):
        # Default pattern, load all 1s
        if pattern == "":
            pattern = "1"*self.clipSize
        # Antibug
        if len(str(pattern)) > self.clipSize: pattern = pattern[:self.clipSize]
        # Loading
        newClip = []
        for char in pattern:
            if not self.allowStrPattern:
                newClip.append(int(char))
            else:
                newClip.append(char)
        self.clip = newClip
    def ammoCount(self):
        if self.allowStrPattern:
            return -1
        else:
            return self.clipSize - self.clip.count(0)

def help():
    print("https://pypi.org/project/rusrul-lib/")