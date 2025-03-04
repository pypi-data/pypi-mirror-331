from likeprocessing.processing import *
import pygame



class ImageAnimee:
    def __init__(self):
        self.images = {}
        self.index_animation = 0
        self.compteur_animation = 0
        self.vitesse = 5

    def add_images(self, name, image0:str,fin:int):
        """ajoute une liste d'images à un nom"""
        prefixe = image0.split("0")[0]
        suffixe = image0.split("0")[1]
        self.images[name] = [loadImage(prefixe + str(i) + suffixe) for i in range(fin+1)]

    def animer(self,name):
        self.compteur_animation += 1
        if self.compteur_animation % self.vitesse == 0:
            self.index_animation = (self.index_animation + 1) % len(self.images[name])
            self.compteur_animation = 0
        return self.images[name][self.index_animation]

    def get_width(self):
        name = list(self.images.keys())[0]
        return self.images[name].get_width()

    def get_height(self):
        name = list(self.images.keys())[0]
        return self.images[name].get_height()

class BoxContainer:
    """Créé un conteneur d'objet"""
    def __init__(self):
        self.objets = []
        self.index = 0

    def ajouter(self, objet):
        """
        Ajoute un objet au conteneur.

        :param objet: L'objet à ajouter.
        """
        self.objets.append(objet)

    def retirer(self, objet):
        """
        Retire un objet du conteneur.

        :param objet: L'objet à retirer.
        """
        self.objets.remove(objet)

    def draw(self):
        """
        Dessine tous les objets visibles dans le conteneur.
        """
        for objet in self.objets:
            if hasattr(objet, 'draw') and callable(getattr(objet, 'draw')):
                objet.draw()

    def move(self):
        """
        Déplace tous les objets mobiles dans le conteneur.
        """
        for objet in self.objets:
            if isinstance(objet, MovableBox) or isinstance(objet, MovableGravityBox):
                objet.move()

    def find(self, name):
        """
        Recherche un objet par type.

        :param type: Le type d'objet à rechercher.
        :return: L'objet trouvé ou None.
        """
        for objet in self.objets:
            if hasattr(objet, 'name') and objet.name == name:
                return objet
        return None

    def __iter__(self):
        """
        Retourne l'objet lui-même comme itérateur.
        """
        self.index = 0  # Réinitialise l'index pour une nouvelle itération
        return self

    def __next__(self):
        """
        Retourne l'objet suivant dans l'itération.
        """
        if self.index < len(self.objets):
            result = self.objets[self.index]
            self.index += 1
            return result
        else:
            # Lève une exception StopIteration pour signaler la fin de l'itération
            raise StopIteration

class Inventaire(BoxContainer):
    def __init__(self, x=0, y=0):
        super().__init__()
        self.x = x
        self.y = y
        self.visible = False

    def draw(self):
        if self.visible and len(self.objets) > 0:
            rect(self.x, self.y, 60 * len(self.objets), 60, fill="brown", stroke="black", align_h="center",
                 align_v="center")
            for i, objet in enumerate(self.objets):
                objet.x = 10 + i * 60
                objet.y = 10
                objet.draw()

class Box(pygame.Rect):
    debug = False
    def __init__(self, x, y, width, height, image=None, collision_behavior=['stop'],**kwargs):
        """
        Initialise une boîte avec une position, des dimensions, une image, une visibilité,
        un état de collision et une couleur.

        :param x: Coordonnée x du coin supérieur gauche de la boîte.
        :param y: Coordonnée y du coin supérieur gauche de la boîte.
        :param width: Largeur de la boîte.
        :param height: Hauteur de la boîte.
        :param image: Image associée à la boîte (par défaut None).
        """
        self.image_name = None
        if isinstance(image, str):
            self.path_image = image
            self.image = loadImage(image)
        elif isinstance(image, pygame.Surface):
            self.image = image
        elif isinstance(image, ImageAnimee):
            self.image = image
            self.image_name = list(self.image.images.keys())[0]
        else:
            self.image = None
            self.path_image = None
        if image is not None:
            if width == 0:
                width = self.image.get_width()
            if height == 0:
                height = self.image.get_height()


        super().__init__(x, y, width, height)

        self.visible = True
        self.enable_collide = True
        self.color = "white"
        self.collision_behavior = collision_behavior
        self.name = kwargs.get("name","")
        self.fill = kwargs.get("fill")

    def get_position(self):
        """
        Retourne la position (x, y) de la boîte.

        :return: Un tuple (x, y) représentant la position de la boîte.
        """
        return self.x, self.y

    def get_dimensions(self):
        """
        Retourne les dimensions (width, height) de la boîte.

        :return: Un tuple (width, height) représentant les dimensions de la boîte.
        """
        return self.width, self.height

    def set_position(self, x, y):
        """
        Définit une nouvelle position pour la boîte.

        :param x: Nouvelle coordonnée x.
        :param y: Nouvelle coordonnée y.
        """
        self.x = x
        self.y = y

    def set_dimensions(self, width, height):
        """
        Définit de nouvelles dimensions pour la boîte.

        :param width: Nouvelle largeur.
        :param height: Nouvelle hauteur.
        """
        self.width = width
        self.height = height

    def collides_with(self, other_box):
        """
        Vérifie si cette boîte entre en collision avec une autre boîte.

        :param other_box: Une autre instance de Box.
        :return: True si les boîtes se chevauchent, False sinon.
        """
        # return (self.enable_collide and self.x < other_box.x + other_box.width and
        #         self.x + self.width > other_box.x and
        #         self.y < other_box.y + other_box.height and
        #         self.y + self.height > other_box.y)
        # Calcul de l'intersection
        intersection = self.clip(other_box)

        # Si les rectangles ne se chevauchent pas, retourner None
        if intersection.width == 0 or intersection.height == 0:
            return None

        # Déterminer le sens de l'intersection
        if intersection.width > intersection.height:
            # Collision horizontale
            if intersection.top == self.top:
                return "haut"  # self touche other_box par le bas
            if intersection.bottom == self.bottom:
                return "bas"  # self touche other_box par le haut
        else:
            # Collision verticale
            if intersection.left == self.left:
                return "gauche"  # self touche other_box par la droite
            if intersection.right == self.right:
                return "droite" # self touche other_box par la gauche

        return None

    def __repr_(self):
        """
        Retourne une représentation sous forme de chaîne de caractères de la boîte.

        :return: Une chaîne de caractères représentant la boîte.
        """
        return (f"Box(x={self.x}, y={self.y}, width={self.width}, height={self.height}, "
                f"image={self.path_image if self.image else 'none'}, visible={self.visible}, "
                f"enable_collide={self.enable_collide}, color={self.color})")

    def __str__(self):
        return self.name + " " + str(self.collision_behavior)

    def draw(self):
        """
        Dessine la boîte si elle est visible.
        """
        if self.visible:
            if self.image is None and self.fill is not None:
                rect(self.x, self.y, self.width, self.height, fill=self.fill)
            if Box.debug:
                rect(self.x, self.y, self.width, self.height, no_fill=True, stroke=self.color)
            if isinstance(self.image,ImageAnimee):
                img = self.image.animer(self.image_name)
                image(img,self.x-(img.get_width()-self.width)//2,self.y)
            elif self.image is not None:
                image(self.image, self.x - (self.image.get_width() - self.width) // 2, self.y)



class MovableBox(Box):
    def __init__(self, x, y, width, height, image=None, collision_behavior=['stop'], velocity_x=0, velocity_y=0, obstacles:BoxContainer=None, **kwargs):
        """
        Initialise une boîte mobile avec une position, des dimensions, une vélocité et un comportement en cas de collision.

        :param x: Coordonnée x du coin supérieur gauche de la boîte.
        :param y: Coordonnée y du coin supérieur gauche de la boîte.
        :param width: Largeur de la boîte.
        :param height: Hauteur de la boîte.
        :param velocity_x: Vélocité horizontale de la boîte.
        :param velocity_y: Vélocité verticale de la boîte.
        :param collision_behavior: Comportement en cas de collision ('stop', 'bounce', 'stick').
        """
        super().__init__(x, y, width, height, image, collision_behavior, **kwargs)
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.collision_zone = None
        self.obstacles = obstacles
        self.voisins = {"haut":None,"bas":None,"gauche":None,"droite":None}

    def move(self):
        """
        Déplace la boîte en fonction de sa vélocité.
        """
        self.voisins = {"haut": None, "bas": None, "gauche": None, "droite": None}
        if self.velocity_x != 0 or self.velocity_y != 0:
            for obstacle in self.obstacles:
                if obstacle!=self:
                    collision = self.collides_with(obstacle)
                    if collision:
                        self.voisins[collision] = obstacle
            self.check_collision()
            self.x += self.velocity_x
            self.y += self.velocity_y

    def set_velocity(self, velocity_x, velocity_y):
        """
        Définit une nouvelle vélocité pour la boîte.

        :param velocity_x: Nouvelle vélocité horizontale.
        :param velocity_y: Nouvelle vélocité verticale.
        """
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y

    def set_x_velocity(self, velocity_x):
        """
        Définit une nouvelle vélocité horizontale pour la boîte.

        :param velocity_x: Nouvelle vélocité horizontale.
        """
        self.velocity_x = velocity_x

    def set_y_velocity(self, velocity_y):
        """
        Définit une nouvelle vélocité verticale pour la boîte.

        :param velocity_y: Nouvelle vélocité verticale.
        """
        self.velocity_y = velocity_y

    def get_x_velocity(self):
        """
        Retourne la vélocité horizontale de la boîte.

        :return: La vélocité horizontale.
        """
        return self.velocity_x

    def get_y_velocity(self):
        """
        Retourne la vélocité verticale de la boîte.

        :return: La vélocité verticale.
        """
        return self.velocity_y


    def check_collision(self):
        """
        Vérifie et gère la collision avec les autres boîtes en fonction du comportement défini.
        """
        # if self.name == "player":
        #     print([(key,str(value)) for key,value in self.voisins.items()])
        velocity_x = self.velocity_x
        velocity_y = self.velocity_y
        for obstacle in self.voisins.keys():
            if self.voisins[obstacle] is not None:
                if "bounce" in self.voisins[obstacle].collision_behavior or 'bounce' in self.collision_behavior and "stop" in self.voisins[obstacle].collision_behavior :
                    self.velocity_x = -self.velocity_x
                    self.velocity_y = -self.velocity_y
                elif (obstacle=="gauche" or obstacle=="droite") and ("bouncex" in self.voisins[obstacle].collision_behavior or 'bouncex' in self.collision_behavior and "stop" in self.voisins[obstacle].collision_behavior):
                    self.velocity_x = -self.velocity_x
                elif (obstacle=="haut" or obstacle=="bas") and ("bouncey" in self.voisins[obstacle].collision_behavior or 'bouncey' in self.collision_behavior and "stop" in self.voisins[obstacle].collision_behavior):
                    self.velocity_y = -self.velocity_y
                else:
                    if (obstacle=="gauche" or obstacle=="droite") and "stickx" in self.voisins[obstacle].collision_behavior and "mover" in self.collision_behavior:
                        #print(f"mover stickx {self.velocity_x}")
                        if self.velocity_x != 0:
                            #print("mover")
                            if isinstance(self.voisins["bas"],MovableBox):
                                self.voisins[obstacle].velocity_x = self.velocity_x + self.voisins["bas"].velocity_x
                            else:
                                self.voisins[obstacle].velocity_x = self.velocity_x
                            self.voisins[obstacle].move()
                            self.voisins[obstacle].velocity_x = 0
                    if "stop" in self.voisins[obstacle].collision_behavior:
                        if obstacle == "bas" and self.velocity_y > 0:
                            self.velocity_y = 0
                            self.y = self.voisins[obstacle].y - self.height+1
                            if isinstance(self.voisins[obstacle],MovableBox):
                                if self.name == "player":
                                    self.velocity_x += self.voisins[obstacle].velocity_x
                                else:
                                    self.velocity_x = self.voisins[obstacle].velocity_x
                        elif obstacle == "haut" and self.velocity_y < 0:
                            self.velocity_y = 0
                            self.y = self.voisins[obstacle].y + self.voisins[obstacle].height - 1
                        elif obstacle == "droite" and self.velocity_x > 0:
                            self.velocity_x = 0
                            self.x = self.voisins[obstacle].x - self.width + 1
                        elif obstacle == "gauche" and self.velocity_x < 0:
                            self.velocity_x = 0
                            self.x = self.voisins[obstacle].x + self.voisins[obstacle].width - 1
                    elif "stopx" in self.voisins[obstacle].collision_behavior:
                        if obstacle == "droite" and self.velocity_x > 0:
                            self.velocity_x = 0
                            self.x = self.voisins[obstacle].x - self.width + 1
                        elif obstacle == "gauche" and self.velocity_x < 0:
                            self.velocity_x = 0
                            self.x = self.voisins[obstacle].x + self.voisins[obstacle].width - 1
                    elif "stopy" in self.voisins[obstacle].collision_behavior and isinstance(self,MovableGravityBox):
                        if obstacle == "bas" and self.velocity_y > 0:
                            self.velocity_y = 0
                            if isinstance(self.voisins[obstacle], MovableBox):
                                self.velocity_x += self.voisins[obstacle].velocity_x
                                self.x += self.velocity_x
                                self.velocity_x = 0
                            self.y = self.voisins[obstacle].y - self.height+1
                        elif obstacle == "haut" and self.velocity_y < 0:
                            self.velocity_y = 0
                            self.y = self.voisins[obstacle].y + self.voisins[obstacle].height - 1
                    if "event" in self.voisins[obstacle].collision_behavior:
                        self.voisins[obstacle].event(self,self.voisins[obstacle])



    def __repr_(self):
        """
        Retourne une représentation sous forme de chaîne de caractères de la boîte mobile.

        :return: Une chaîne de caractères représentant la boîte mobile.
        """
        return (f"MovableBox(x={self.x}, y={self.y}, width={self.width}, height={self.height}, "
                f"velocity_x={self.velocity_x}, velocity_y={self.velocity_y}, "
                f"collision_behavior='{self.collision_behavior}', image={self.path_image if self.image else 'none'})")


class MovableGravityBox(MovableBox):
    def __init__(self, x, y, width, height, image=None, collision_behavior='stop', velocity_x=0, velocity_y=0, obstacles:BoxContainer=None, gravity=0.11, **kwargs):
        """
        Initialise une boîte mobile avec gravité avec une position, des dimensions, une vélocité,
        un comportement en cas de collision et une gravité.

        :param x: Coordonnée x du coin supérieur gauche de la boîte.
        :param y: Coordonnée y du coin supérieur gauche de la boîte.
        :param width: Largeur de la boîte.
        :param height: Hauteur de la boîte.
        :param velocity_x: Vélocité horizontale de la boîte.
        :param velocity_y: Vélocité verticale de la boîte.
        :param collision_behavior: Comportement en cas de collision ('stop', 'bounce', 'stick').
        :param gravity: Force de gravité appliquée à la boîte.
        """
        super().__init__(x, y, width, height, image, collision_behavior, velocity_x, velocity_y, obstacles, **kwargs)
        self.gravity = gravity
        self.name = ""

    def move(self):
        """
        Déplace la boîte en fonction de sa vélocité et applique la gravité.
        """
        # Appliquer la gravité à la vélocité verticale
        self.velocity_y += self.gravity

        # Mettre à jour la position
        super().move()

    def __repr_(self):
        """
        Retourne une représentation sous forme de chaîne de caractères de la boîte mobile avec gravité.

        :return: Une chaîne de caractères représentant la boîte mobile avec gravité.
        """
        return (f"MovableGravityBox(x={self.x}, y={self.y}, width={self.width}, height={self.height}, "
                f"velocity_x={self.velocity_x}, velocity_y={self.velocity_y}, "
                f"collision_behavior='{self.collision_behavior}', gravity={self.gravity}, "
                f"image={self.path_image if self.image else 'none'})")

class Player(MovableGravityBox):
    def __init__(self, x, y, width, height, image,obstacles,keys={},**kwargs):
        super().__init__(x, y, width, height, image, [],0, 0, obstacles, gravity=0.11,**kwargs)
        self.saut = 0
        self.keys = keys
        if "left" not in self.keys:
            self.keys["left"] = K_LEFT
        if "right" not in self.keys:
            self.keys["right"] = K_RIGHT
        if "jump" not in self.keys:
            self.keys["jump"] = K_SPACE
        if "stick" not in self.keys:
            self.keys["stick"] = K_d
        if "catch" not in self.keys:
            self.keys["catch"] = K_c
        self.name = "player"
        self.sens = "droite"
        self.catch = False
        self.inventaire = Inventaire()

    def scan_keys(self):
        if keyIsDown(self.keys["left"]):
            self.set_x_velocity(-2)
            self.sens = "gauche"
        elif keyIsDown(self.keys["right"]):
            self.set_x_velocity(2)
            self.sens = "droite"
        else:
            self.set_x_velocity(0)
        if keyIsDown(self.keys["jump"]) and self.saut == 0:
            self.saut = 1
            if self.velocity_y == 0:
                self.set_y_velocity(-6)
        else:
            self.saut = 0
        if keyIsDown(self.keys["stick"]) and "sticky" not in self.collision_behavior:
            self.collision_behavior.append('mover')
        else:
            self.collision_behavior = [x for x in self.collision_behavior if x != 'mover']
        if keyIsDown(self.keys["catch"]):
            self.catch = True
        else:
            self.catch = False

    def draw(self):
        if self.velocity_x != 0:
            self.image_name = "marche"
        else:
            self.image_name = "idle"
        if self.visible:
            if Box.debug:
                rect(self.x, self.y, self.width, self.height, no_fill=True, stroke=self.color)
            if isinstance(self.image,ImageAnimee):
                img = self.image.animer(self.image_name)
                image(img,self.x-(img.get_width()-self.width)//2,self.y,flip_h=(self.sens == "gauche"))
            elif self.image is not None:
                image(self.image, self.x - (self.image.get_width() - self.width) // 2, self.y)
        if self.inventaire.visible:
            self.inventaire.draw()

class EventBox(Box):
    def __init__(self, x, y, width, height, name, image=None,event=None, **kwargs):
        """ Initialise une boîte événementielle avec une position, des dimensions, un nom, une image et un événement.
        event est une fonction qui prend deux arguments: player et objet.
        player est l'objet qui a déclenché l'événement et objet est l'objet sur lequel l'événement est déclenché."""
        collision_behavior = kwargs.get("collision_behavior",['event'])
        if "event" not in collision_behavior:
            collision_behavior.append("event")
        super().__init__(x, y, width, height, image,collision_behavior)
        if isinstance(event, str):
            self.event = eval(event)
        else:
            self.event = event
        self.name = name


import json
class Ball(MovableBox):
    def __init__(self,x,y,width,height,image,velocity_x,velocity_y,obstacles,**kwargs):
        """Initialise une balle avec une position, des dimensions, une image, une vélocité en x et en y et des obstacles (BoxContainer)."""
        super().__init__(x,y,width,height,image,["bouncex","bouncey"],velocity_x,velocity_y,obstacles,**kwargs)

    def move(self):
        super().move()

    def draw(self):
        if self.visible:
            if self.image is None:
                ellipse(self.x,self.y,self.width,self.height,fill=self.fill)
            else:
                super().draw()

class Levier(EventBox):
    def __init__(self,x,y,width,height,images:list,event,pos=0):
        """Initialise un levier avec une position, des dimensions, une liste d'images et un événement. Le nombre de positions est défini par le nombre d'images."""
        super().__init__(x,y,width,height,"levier",images[0],event)
        self.images = []
        for img in images:
            if isinstance(img,str):
                self.images.append(loadImage(img))
            else:
                self.images=img
        self.pos = pos
        self.enable = True

    def set_pos(self,pos):
        """Définit la position du levier."""
        if self.enable:
            self.pos = pos%len(self.images)
            self.image = self.images[self.pos]

class Level:
    def __init__(self,player,config, number=0):
        self.config_all = config
        self.config = self.config_all[number]
        self.number = self.config['number']
        self.player = player
        self.obstacles = BoxContainer()
        self.events = events
        self.completed = False
        # self.event_fonctions = event_functions
        # self.setup()
        # self.player.obstacles = self.obstacles


    def setup(self,globales):
        self.player.set_position(*self.config['player_position'])
        self.obstacles.objets.clear()
        for obstacle_config in self.config['obstacles']:
            obstacle_type = obstacle_config.pop('type')
            if obstacle_type == "Box":
                self.obstacles.ajouter(Box(**obstacle_config))
            elif obstacle_type == "MovableBox":
                self.obstacles.ajouter(MovableBox(obstacles=self.obstacles, **obstacle_config))
            elif obstacle_type == "EventBox":
                event_name = obstacle_config.pop('event')
                event_function = globales.get(event_name)
                if event_function is not None:
                    self.obstacles.ajouter(EventBox(event=event_function, **obstacle_config))
                else:
                    print(f"Warning: Event function '{event_name}' is not defined.")
        self.player.obstacles = self.obstacles

    def update(self):
        self.player.scan_keys()
        self.player.move()
        self.obstacles.move()

    def draw(self):
        self.obstacles.draw()
        self.player.draw()

    def check_completion(self):
        condition = self.config['completion_condition']
        if condition['type'] == 'position':
            x = condition.get("x",False)
            y = condition.get("y",False)
            if x and y and self.player.x > x and self.player.y > y:
                self.completed = True
            elif x and self.player.x > x:
                self.completed = True
            elif y and self.player.y > y:
                self.completed = True
        elif condition['type'] == 'inventory':
            if any(objet.name == condition['item'] for objet in self.player.inventaire.objets):
                self.completed = True

    def next_level(self):
        if self.completed:
            level =  Level(self.player,self.config_all,number=self.number)
            level.setup(globals())
            return level
        return self



