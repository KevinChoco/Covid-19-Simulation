import pygame
import random
import math
import keyboard

# Settings
WIDTH, HEIGHT = 800, 800
NUM_PEOPLE = 50
PERSON_RADIUS = 4
SPEED = 2
MIN_DIST = 20
INFECTION_RADIUS = 30
INFECTION_CHANCE = 0.2
INFECTION_DURATION = 200

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Social Distancing Simulation")
clock = pygame.time.Clock()

class Person:
    def __init__(self):
        self.x = random.uniform(0, WIDTH)
        self.y = random.uniform(0, HEIGHT)
        angle = random.uniform(0, 2 * math.pi)
        self.vx = math.cos(angle) * SPEED
        self.vy = math.sin(angle) * SPEED
        self.status = "Healthy"
        self.infection_time = 0

    def move(self):
        self.x += self.vx
        self.y += self.vy

        if self.x < 0 or self.x > WIDTH:
            self.vx *= -1
        if self.y < 0 or self.y > HEIGHT:
            self.vy *= -1

    def distance_to(self, other):
        return math.hypot(self.x - other.x, self.y - other.y)

    def avoid_others(self, people):
        move_x, move_y = 0, 0
        for other in people:
            if other == self:
                continue
            dist = self.distance_to(other)
            if dist < MIN_DIST:
                dx = self.x - other.x
                dy = self.y - other.y
                move_x += dx / dist
                move_y += dy / dist

        length = math.hypot(move_x, move_y)
        if length > 0:
            self.vx += (move_x / length) * 0.5
            self.vy += (move_y / length) * 0.5

        speed = math.hypot(self.vx, self.vy)
        if speed > SPEED:
            self.vx = (self.vx / speed) * SPEED
            self.vy = (self.vy / speed) * SPEED

    def try_infect(self, people):
        pass  # Overridden in subclasses

class InfectedPerson(Person):
    def __init__(self):
        super().__init__()
        self.status = "Infected"

    def try_infect(self, people):
        self.infection_time += 1
        if self.infection_time > INFECTION_DURATION:
            return ImmunePerson(self.x, self.y, self.vx, self.vy)

        for other in people:
            if other == self or other.status != "Healthy":
                continue
            if self.distance_to(other) < INFECTION_RADIUS and random.random() < INFECTION_CHANCE:
                people[people.index(other)] = InfectedPerson.from_person(other)
        return self

    
    def from_person(person):
        p = InfectedPerson()
        p.x, p.y, p.vx, p.vy = person.x, person.y, person.vx, person.vy
        return p

class ImmunePerson(Person):
    def __init__(self, x, y, vx, vy):
        super().__init__()
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.status = "Immune"

class HealthyPerson(Person):
    def __init__(self):
        super().__init__()

# Start with one infected, rest healthy
people = [InfectedPerson()] + [HealthyPerson() for _ in range(NUM_PEOPLE - 1)]

def draw_counters():
    healthy = sum(1 for p in people if p.status == "Healthy")
    infected = sum(1 for p in people if p.status == "Infected")
    immune = sum(1 for p in people if p.status == "Immune")

    font = pygame.font.SysFont('Arial', 24)
    screen.blit(font.render(f"Healthy: {healthy}", True, (0, 0, 0)), (10, 10))
    screen.blit(font.render(f"Infected: {infected}", True, (0, 0, 0)), (10, 40))
    screen.blit(font.render(f"Immune: {immune}", True, (0, 0, 0)), (10, 70))

running = True
while running:
    clock.tick(60)
    screen.fill((255, 255, 255))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if keyboard.is_pressed('down'):
        pygame.quit()
        exit()

    for person in people:
        person.avoid_others(people)

    new_people = []
    for person in people:
        updated = person.try_infect(people)
        new_people.append(updated if updated else person)
    people = new_people

    for person in people:
        person.move()
        color = (0, 0, 255) if person.status == "Healthy" else (255, 0, 0) if person.status == "Infected" else (0, 255, 0)
        pygame.draw.circle(screen, color, (int(person.x), int(person.y)), PERSON_RADIUS)
        if person.status == "Infected":
            pygame.draw.circle(screen, (255, 0, 0), (int(person.x), int(person.y)), INFECTION_RADIUS, 1)

    draw_counters()
    pygame.display.flip()

pygame.quit()
