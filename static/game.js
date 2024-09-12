let game;
const ratio = Math.max(window.innerWidth / window.innerHeight, window.innerHeight / window.innerWidth);
const DEFAULT_HEIGHT = 600;
const DEFAULT_WIDTH = ratio * DEFAULT_HEIGHT;
let gameOptions = {
    // start vertical point of the terrain, 0 = very top; 1 = very bottom
    startTerrainHeight: 0.5,
    // max slope amplitude, in pixels
    amplitude: 300,
    // slope length range, in pixels
    slopeLength: [300, 600],
    // a mountain is a a group of slopes.
    mountainsAmount: 3,
    // amount of slopes for each mountain
    slopesPerMountain: 6,
    // positive and negative car acceleration
    carAcceleration: [0.01, -0.005],
    // maximum car velocity
    maxCarVelocity: 0.4,
    // mountain colors
    mountainColors: [0x853c35, 0x763530],
    // line width for each mountain color, in pixels
    mountainColorsLineWidth: [0, 200]
}

async function upd_score(coins) {
    let params = new URLSearchParams(document.location.search);
    await fetch("/game/update_score", {
        method: "POST",
        headers: {
            'Content-Type': 'application/json;charset=utf-8'
        },
        body: JSON.stringify({ user_id: params.get('user_id'), score: coins, message_id: params.get('message_id') })
    });
}

function loadFont(name, url) {
    let newFont = new FontFace(name, `url(${url})`);
    newFont.load().then(function(loaded) {
        document.fonts.add(loaded);
    }).catch(function(error) {
        return error;
    });
}
window.addEventListener("orientationchange", function() {
    document.location.reload();
});
window.onload = function() {
    let gameConfig = {
        type: Phaser.AUTO,
        scale: {
            mode: Phaser.Scale.FIT,
            autoCenter: Phaser.Scale.CENTER_BOTH,
            parent: "thegame",
            width: DEFAULT_WIDTH,
            height: DEFAULT_HEIGHT
        },
        physics: {
            default: "matter",
            matter: {
                debug: false,
                debugBodyColor: 0x000000,
            }
        },
        scene: playGame
    }
    game = new Phaser.Game(gameConfig);
    window.focus();
}

class playGame extends Phaser.Scene {
    constructor() {
        super("PlayGame");
    }
    preload() {
        let progressBar = this.add.graphics();
        let progressBox = this.add.graphics();
        progressBox.fillStyle(0x222222, 0.8);
        const h = 100;
        const w = 840;
        const x = game.config.width / 2 - w / 2;
        const y = game.config.height / 2 - h / 2;
        progressBox.fillRect(x, y, w, h);

        this.load.on('progress', function(value) {
            progressBar.clear();
            progressBar.fillStyle(0xffffff, 1);
            progressBar.fillRect(x + 20, y + 20, (w - 40) * value, h - 40);
        });
        this.load.on('complete', function() {
            progressBar.destroy();
            progressBox.destroy();
        });

        this.load.image("pizza", "static/pizza.png");
        this.load.image("buhanka", "static/buhanka.png");
        this.load.image("background", "static/background.png");
        this.load.spritesheet("coin", "static/coinsheet.png", {
            frameWidth: 225,
            frameHeight: 225
        });
        loadFont("pixelfont", "static/PixelCyrNormal.ttf");
        this.load.audio("sndCollect", "static/collect.mp3");
        this.load.audio("sndDeath", "static/death.mp3");
        this.load.audio("sndMonodori", "static/monodori.mp3");
    }
    create() {
        this.sndCollect = this.sound.add("sndCollect", { loop: false, volume: 0.5 });
        this.sndDeath = this.sound.add("sndDeath", { loop: false, volume: 1 });
        this.sndMonodori = this.sound.add("sndMonodori", { loop: true, volume: 1 });
        this.sndMonodori.play();
        this.add.sprite(0, 0, 'background').setScrollFactor(0).setOrigin(0, 0).setDisplaySize(game.config.width, game.config.height);
        this.anims.create({
            key: "animCoin",
            frames: this.anims.generateFrameNumbers("coin"),
            frameRate: 10,
            repeat: -1
        });
        this.dead = false;
        this.coindist = 0;
        this.coins = 0;
        this.rocksRatio = 5;
        // creation of pool arrays
        this.bodyPool = [];
        this.rocksPool = [];

        // array to store mountains
        this.mountainGraphics = [];

        // mountain start coordinates
        this.mountainStart = new Phaser.Math.Vector2(0, 0);

        // loop through all mountains
        for (let i = 0; i < gameOptions.mountainsAmount; i++) {

            // each mountain is a graphics object
            this.mountainGraphics[i] = this.add.graphics();

            // generateTerrain is the method to generate the terrain. The arguments are the graphics object and the start position
            this.mountainStart = this.generateTerrain(this.mountainGraphics[i], this.mountainStart);
        }

        // method to add the car
        this.addCar();

        // input management
        this.input.on("pointerdown", this.accelerate, this);
        this.input.on("pointerup", this.decelerate, this);
        // car initial velocity
        this.velocity = 0;

        // car initial acceleration
        this.acceleration = 0;
        // text object with terrain information
        this.coinInfo = this.add.text(this.game.config.width * 0.5, 70, "0", {
            fontFamily: "pixelfont",
            fontSize: 80,
            fontStyle: 'bold',
            color: "#f5f5f5",
            align: 'center'
        });
        this.coinInfo.setOrigin(0.5);
        this.matter.world.on("collisionstart", function(event, bodyA, bodyB) {
            if ((bodyA.label == "car" && bodyB.label == "ground") || (bodyB.label == "car" && bodyA.label == "ground") ||
                (bodyA.label == "car" && bodyB.label == "rock") || (bodyB.label == "car" && bodyA.label == "rock")) {
                if (!this.dead) {
                    this.matter.world.removeConstraint(this.c1);
                    this.matter.world.removeConstraint(this.c2);
                    this.matter.world.removeConstraint(this.c3);
                    this.matter.world.removeConstraint(this.c4);
                    this.rearWheel.setBounce(1);
                    this.frontWheel.setBounce(1);
                    this.sndMonodori.stop();
                    this.sndDeath.play();
                    this.dead = true;
                    this.time.delayedCall(4000, () => {
                        upd_score(this.coins);
                        this.scene.restart();
                    });
                }
            } else if ((bodyA.label == "car" && bodyB.label == "coin") || (bodyB.label == "car" && bodyA.label == "coin") ||
                (bodyA.label == "wheel" && bodyB.label == "coin") || (bodyB.label == "wheel" && bodyA.label == "coin")) {
                if (bodyA.label == "coin")
                    bodyA.gameObject.destroy();
                else if (bodyB.label == "coin")
                    bodyB.gameObject.destroy();
                this.sndCollect.play();
                this.coins += 1;
                this.rocksRatio = 5 + Math.floor(this.coins / 5);
                if (this.rocksRatio > 30)
                    this.rocksRatio = 30;
            }
        }.bind(this));
    }

    // method to generate the terrain. Arguments: the graphics object and the start position
    generateTerrain(graphics, mountainStart) {
        // place graphics object
        graphics.x = mountainStart.x;
        // draw the ground
        graphics.clear();
        // array to store slope points
        let slopePoints = [];
        // variable to count the amount of slopes
        let slopes = 0;

        // slope start point
        let slopeStart = new Phaser.Math.Vector2(0, mountainStart.y);

        // set a random slope length
        const slopeLength = Phaser.Math.Between(gameOptions.slopeLength[0], gameOptions.slopeLength[1]);

        // determine slope end point, with an exception if this is the first slope of the fist mountain: we want it to be flat
        let slopeEnd = (mountainStart.x == 0) ? new Phaser.Math.Vector2(slopeStart.x + gameOptions.slopeLength[1] * 1.5, 0) : new Phaser.Math.Vector2(slopeStart.x + slopeLength, Math.random());

        // current horizontal point
        let pointX = 0;
        // while we have less slopes than regular slopes amount per mountain...
        while (slopes < gameOptions.slopesPerMountain) {

            // slope interpolation value
            let interpolationVal = this.interpolate(slopeStart.y, slopeEnd.y, (pointX - slopeStart.x) / (slopeEnd.x - slopeStart.x));

            // if current point is at the end of the slope...
            if (pointX == slopeEnd.x) {

                // increase slopes amount
                slopes++;

                // next slope start position
                slopeStart = new Phaser.Math.Vector2(pointX, slopeEnd.y);

                // next slope end position
                slopeEnd = new Phaser.Math.Vector2(slopeEnd.x + Phaser.Math.Between(gameOptions.slopeLength[0], gameOptions.slopeLength[1]), Math.random());

                // no need to interpolate, we use slope start y value
                interpolationVal = slopeStart.y;
            }

            // current vertical point
            let pointY = game.config.height * gameOptions.startTerrainHeight + interpolationVal * gameOptions.amplitude;

            // add new point to slopePoints array
            slopePoints.push(new Phaser.Math.Vector2(pointX, pointY));
            // move on to next point
            pointX++;
        }

        // simplify the slope
        let simpleSlope = simplify(slopePoints, 1, true);

        // loop through all simpleSlope points starting from the second
        for (let i = 1; i < simpleSlope.length; i++) {

            // define a line between previous and current simpleSlope points
            let line = new Phaser.Geom.Line(simpleSlope[i - 1].x, simpleSlope[i - 1].y, simpleSlope[i].x, simpleSlope[i].y);

            // calculate line length, which is the distance between the two points
            let distance = Phaser.Geom.Line.Length(line);

            // calculate the center of the line
            let center = Phaser.Geom.Line.GetPoint(line, 0.5);

            // calculate line angle
            let angle = Phaser.Geom.Line.Angle(line);

            // if the pool is empty...
            if (this.bodyPool.length == 0) {

                // create a new rectangle body
                let body = this.matter.add.rectangle(center.x + mountainStart.x, center.y, distance, 10, {
                    label: 'ground',
                    isStatic: true,
                    angle: angle,
                    friction: 1,
                    restitution: 0
                });
                body.inPool = false;
            }

            // if the pool is not empty...
            else {

                // get the body from the pool
                let body = this.bodyPool.shift();
                body.inPool = false;

                // reset, reshape and move the body to its new position
                this.matter.body.setPosition(body, {
                    x: center.x + mountainStart.x,
                    y: center.y
                });
                let length = body.area / 10;
                this.matter.body.setAngle(body, 0)
                this.matter.body.scale(body, 1 / length, 1);
                this.matter.body.scale(body, distance, 1);
                this.matter.body.setAngle(body, angle);

            }
            this.coindist += 1;
            if (this.coindist >= 20) {
                this.coindist = 0;
                let coin = this.matter.add.sprite(center.x + mountainStart.x, center.y - 70, 'coin');
                coin.setDisplaySize(60, 60);
                coin.setCircle(30, {
                    label: 'coin',
                    isStatic: true,
                    friction: 1,
                    restitution: 0,
                    isSensor: true
                });
                coin.anims.play('animCoin', true);
            }
            // should we add a rock?
            if (Phaser.Math.Between(0, 100) < this.rocksRatio && (mountainStart.x > 0 || i != 1)) {

                // random rock position
                let size = Phaser.Math.Between(20, 30)
                let depth = Phaser.Math.Between(0, size / 2)
                let rockX = center.x + mountainStart.x + depth * Math.cos(angle + Math.PI / 2);
                let rockY = center.y + depth * Math.sin(angle + Math.PI / 2) - 5;

                // draw the rock
                graphics.fillStyle(0xd16c41, 1);
                graphics.fillCircle(rockX - mountainStart.x, rockY, size);

                // if the pool is empty...
                if (this.rocksPool.length == 0) {

                    // create a new circle body
                    let rock = this.matter.add.circle(rockX, rockY, size, {
                        isStatic: true,
                        angle: angle,
                        friction: 1,
                        restitution: 0,
                        label: "rock"
                    });

                    // assign inPool property to check if the body is in the pool
                    rock.inPool = false;
                } else {

                    // get the rock from the pool
                    let rock = this.rocksPool.shift();

                    // resize the rock
                    this.matter.body.scale(rock, size / rock.circleRadius, size / rock.circleRadius);

                    // move the rock to its new position
                    this.matter.body.setPosition(rock, {
                        x: rockX,
                        y: rockY
                    });
                    rock.inPool = false;
                }
            }
        }
        // new way to draw the slopes
        for (let i = 0; i < gameOptions.mountainColors.length; i++) {
            graphics.moveTo(0, game.config.height * 2);
            graphics.fillStyle(gameOptions.mountainColors[i]);
            graphics.beginPath();
            simpleSlope.forEach(function(point) {
                graphics.lineTo(point.x, point.y + gameOptions.mountainColorsLineWidth[i]);
            }.bind(this))
            graphics.lineTo(simpleSlope[simpleSlope.length - 1].x, game.config.height * 2);
            graphics.lineTo(0, game.config.height * 2);
            graphics.closePath();
            graphics.fillPath();
        }


        // draw the grass
        graphics.lineStyle(16, 0xd67a52);
        graphics.beginPath();
        simpleSlope.forEach(function(point) {
            graphics.lineTo(point.x, point.y);
        })
        graphics.strokePath();

        // assign a custom "width" property to the graphics object
        graphics.width = pointX - 1

        // return the coordinates of last mountain point
        return new Phaser.Math.Vector2(graphics.x + pointX - 1, slopeStart.y);
    }

    // method to build the car
    addCar() {
        // add car body
        this.body = this.matter.add.sprite(game.config.width / 8, 0, 'buhanka');
        this.body.setDisplaySize(220, 88);
        this.body.setRectangle(170, 40, {
            label: 'car',
            friction: 1,
            restitution: 0,
            density: 0.005
        });
        // add front wheel. I used an octagon rather than a circle just to let you see wheel movement
        this.frontWheel = this.matter.add.sprite(game.config.width / 8 + 25, 25, 'pizza');
        this.frontWheel.setDisplaySize(60, 60);
        this.frontWheel.setCircle(30, {
            label: 'wheel',
            friction: 1,
            restitution: 0,
            density: 0.005
        });
        // add rear wheel
        this.rearWheel = this.matter.add.sprite(game.config.width / 8 - 25, 25, 'pizza');
        this.rearWheel.setDisplaySize(60, 60);
        this.rearWheel.setCircle(30, {
            label: 'wheel',
            friction: 1,
            restitution: 0,
            density: 0.005
        });


        // these two constraints will bind front wheel to the body
        this.c1 = this.matter.add.constraint(this.body, this.frontWheel, 50, 0.2, {
            pointA: {
                x: 45,
                y: 15
            }
        });
        this.c2 = this.matter.add.constraint(this.body, this.frontWheel, 50, 0.2, {
            pointA: {
                x: 80,
                y: 15
            }
        });

        // same thing for rear wheel
        this.c3 = this.matter.add.constraint(this.body, this.rearWheel, 50, 0.2, {
            pointA: {
                x: -42,
                y: 15
            }
        });
        this.c4 = this.matter.add.constraint(this.body, this.rearWheel, 50, 0.2, {
            pointA: {
                x: -77,
                y: 15
            }
        });
    }

    // method to accelerate
    accelerate() {
        this.acceleration = gameOptions.carAcceleration[0]
    }

    // method to decelerate
    decelerate() {
        this.acceleration = gameOptions.carAcceleration[1]
    }
    update() {

        // make the game follow the car
        this.cameras.main.scrollX = this.body.x - game.config.width / 8

        // adjust velocity according to acceleration
        this.velocity += this.acceleration;
        this.velocity = Phaser.Math.Clamp(this.velocity, 0, gameOptions.maxCarVelocity);

        // set angular velocity to wheels
        //this.matter.body.setAngularVelocity(this.rearWheel, this.velocity);
        if (!this.dead) {
            this.rearWheel.setAngularVelocity(this.velocity);
            this.frontWheel.setAngularVelocity(this.velocity);
        }
        // loop through all mountains
        this.mountainGraphics.forEach(function(item) {

            // if the mountain leaves the screen to the left...
            if (this.cameras.main.scrollX > item.x + item.width + 100) {

                // reuse the mountain
                this.mountainStart = this.generateTerrain(item, this.mountainStart);
            }
        }.bind(this));

        // get all bodies
        const bodies = this.matter.world.localWorld.bodies;

        // loop through all bodies
        bodies.forEach(function(body) {

            // if the body is out of camera view to the left side and is not yet in the pool..
            if (this.cameras.main.scrollX > body.position.x + 200 && !body.inPool) {
                // ...add the body to the pool
                switch (body.label) {
                    case "ground":
                        this.bodyPool.push(body);
                        break;
                    case "rock":
                        this.rocksPool.push(body);
                        break;
                }
                body.inPool = true;
            }
        }.bind(this))

        // update terrain info text
        this.coinInfo.x = this.cameras.main.scrollX + this.game.config.width * 0.5;
        this.coinInfo.setText(this.coins);
    }
    // method to apply a cosine interpolation between two points
    interpolate(vFrom, vTo, delta) {
        const interpolation = (1 - Math.cos(delta * Math.PI)) * 0.5;
        return vFrom * (1 - interpolation) + vTo * interpolation;
    }
}