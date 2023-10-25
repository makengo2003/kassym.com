var flkty = new Flickity('.slides', {
    autoPlay: 5000,
    wrapAround: true,
    prevNextButtons: false,
    selectedAttraction: 0.015,
    friction: 0.3,
});

flkty.on('pointerUp', function (event, pointer) {
    flkty.player.play();
});
