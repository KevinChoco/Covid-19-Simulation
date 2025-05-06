import pygame
import random
import math
import keyboard 

# settings
WIDTH, HEIGHT = 800, 800
NUM_PEOPLE = 50
PERSON_RADIUS = 4
SPEED = 2
MIN_DIST = 20  # social distance
INFECTION_RADIUS = 30  
INFECTION_CHANCE = 0.2 
INFECTION_DURATION = 200   

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Social Distancing Simulation with Infection")
clock = pygame.time.Clock()

# Person class
class Person:
    def __init__(self, is_infected=False):
        self.x = random.uniform(0, WIDTH)
        self.y = random.uniform(0, HEIGHT)
        angle = random.uniform(0, 2 * math.pi)
        self.vx = math.cos(angle) * SPEED
        self.vy = math.sin(angle) * SPEED
        self.is_infected = is_infected  
        self.is_immune = False  # Check if the person is immune
        self.infection_time = 0  # track duration of sick person

    def move(self):
        self.x += self.vx
        self.y += self.vy

        # Bounce off walls
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
            if dist < MIN_DIST and dist > 0:
                # Move away from the other person
                dx = self.x - other.x
                dy = self.y - other.y
                move_x += dx / dist
                move_y += dy / dist

        # velocity
        length = math.hypot(move_x, move_y)
        if length > 0:
            self.vx += (move_x / length) * 0.5
            self.vy += (move_y / length) * 0.5

        # speed limit
        speed = math.hypot(self.vx, self.vy)
        if speed > SPEED:
            self.vx = (self.vx / speed) * SPEED
            self.vy = (self.vy / speed) * SPEED

    def try_infect(self, people):
        # Check if self is sick, if so add duration to timer
        if self.is_infected and not self.is_immune:
            self.infection_time += 1  # add to infection time

            # Check if the person should recover yet
            if self.infection_time > INFECTION_DURATION:
                self.is_infected = False
                self.is_immune = True  
                self.infection_time = 0  

            for other in people:
                if other == self:
                    continue
                dist = self.distance_to(other)
                if dist < INFECTION_RADIUS and not other.is_infected and not other.is_immune:
                    # 20% chance of spreading sickness
                    if random.random() < INFECTION_CHANCE:
                        other.is_infected = True

# List of people plus 1 sick person
people = [Person(is_infected=True)] + [Person() for _ in range(NUM_PEOPLE - 1)]

# Draw state counter
def draw_counters():
    healthy_count = sum(1 for person in people if not person.is_infected and not person.is_immune)
    infected_count = sum(1 for person in people if person.is_infected)
    immune_count = sum(1 for person in people if person.is_immune)

    # Define font and colors
    font = pygame.font.SysFont('Arial', 24)
    color = (0, 0, 0)  # Black color for text

    # Render the text
    healthy_text = font.render(f"Healthy: {healthy_count}", True, color)
    infected_text = font.render(f"Infected: {infected_count}", True, color)
    immune_text = font.render(f"Immune: {immune_count}", True, color)

    # Draw the text on the screen
    screen.blit(healthy_text, (10, 10))
    screen.blit(infected_text, (10, 40))
    screen.blit(immune_text, (10, 70))

# Main loop
running = True
while running:
    time_delta = clock.tick(60) / 1000.0
    screen.fill((255, 255, 255))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Exit game
    if keyboard.is_pressed('down'):
        pygame.quit()
        exit()

    for person in people:
        person.avoid_others(people)
        person.try_infect(people)

    for person in people:
        person.move()

        # Draw the person based on their state
        if person.is_infected:
            pygame.draw.circle(screen, (255, 0, 0), (int(person.x), int(person.y)), PERSON_RADIUS)
            
            pygame.draw.circle(screen, (255, 0, 0), (int(person.x), int(person.y)), INFECTION_RADIUS, 1)# Circle for infection radius
        elif person.is_immune:
            pygame.draw.circle(screen, (0, 255, 0), (int(person.x), int(person.y)), PERSON_RADIUS)  # Green for immune
        else:
            pygame.draw.circle(screen, (0, 0, 255), (int(person.x), int(person.y)), PERSON_RADIUS)  # Blue for healthy

    
    draw_counters()

    pygame.display.flip()

pygame.quit()
