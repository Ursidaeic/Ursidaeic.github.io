/*
	Miniport by HTML5 UP
	html5up.net | @ajlkn
	Free for personal and commercial use under the CCA 3.0 license (html5up.net/license)
*/

(function($) {

	var	$window = $(window),
		$body = $('body'),
		$nav = $('#nav');

	// Breakpoints.
		breakpoints({
			xlarge:  [ '1281px',  '1680px' ],
			large:   [ '981px',   '1280px' ],
			medium:  [ '737px',   '980px'  ],
			small:   [ null,      '736px'  ]
		});

	// Play initial animations on page load.
		$window.on('load', function() {
			window.setTimeout(function() {
				$body.removeClass('is-preload');
			}, 100);
		});

	// Scrolly.
		$('#nav a, .scrolly').scrolly({
			speed: 1000,
			offset: function() { return $nav.height(); }
		});

})(jQuery);



document.querySelectorAll(".carousel").forEach((carousel) => {
	const items = carousel.querySelectorAll(".carousel__item");
	const buttonsHtml = Array.from(items, () => {
		return `<span class="carousel__button"></span>`;
	});
	carousel.insertAdjacentHTML(
	"afterbegin", 
	`
		<div class="carousel__nav__top">
			${buttonsHtml.join("")}
		</div>
	`);
	carousel.insertAdjacentHTML(
		"beforeend", 
		`
			<div class="carousel__nav__bottom">
				${buttonsHtml.join("")}
			</div>
		`);

	const buttons = carousel.querySelectorAll(".carousel__button");
	const topButtons = Array.from(buttons).slice(0, 3);
	const bottomButtons = Array.from(buttons).slice(3);

	for (let i=0; i<3; i++) {
		topButtons[i].addEventListener("click", () => {
			items.forEach((item) => 
				item.classList.remove("carousel__item--selected")
			);
			topButtons.forEach((button) => 
				button.classList.remove("carousel__button--selected")
			);
			bottomButtons.forEach((button) => 
				button.classList.remove("carousel__button--selected")
			);
			topButtons[i].classList.add("carousel__button--selected");
			bottomButtons[i].classList.add("carousel__button--selected");
			items[i].classList.add("carousel__item--selected");
		
		});
		bottomButtons[i].addEventListener("click", () => {
			items.forEach((item) => 
				item.classList.remove("carousel__item--selected")
			);
			topButtons.forEach((button) => 
				button.classList.remove("carousel__button--selected")
			);
			bottomButtons.forEach((button) => 
				button.classList.remove("carousel__button--selected")
			);
			topButtons[i].classList.add("carousel__button--selected");
			bottomButtons[i].classList.add("carousel__button--selected");
			items[i].classList.add("carousel__item--selected");
			var elmntToView = document.getElementById("casestudies");
			elmntToView.scrollIntoView({behavior: "smooth"}); 
		});

	items[0].classList.add("carousel__item--selected")
	topButtons[0].classList.add("carousel__button--selected")
	bottomButtons[0].classList.add("carousel__button--selected")
	};
});
	// topButtons.forEach((button, i) => {
	// 	button.addEventListener("click", () => {
	// 		//unselect all the items
	// 		items.forEach((item) => 
	// 			item.classList.remove("carousel__item--selected")
	// 		);
	// 		topButtons.forEach((button) => 
	// 			button.classList.remove("carousel__button--selected")
	// 		);
	// 		items[i].classList.add("carousel__item--selected");
	// 		topButtons[i].classList.add("carousel__button--selected");
	// 		bottomButtons[i].classList.add("carousel__button--selected");
	// 	});
	// });
	
	// bottomButtons.forEach((button, i) => {
	// 	button.addEventListener("click", () => {
	// 		//unselect all the items
	// 		items.forEach((item) => 
	// 			item.classList.remove("carousel__item--selected")
	// 		);
	// 		bottomButtons.forEach((button) => 
	// 			button.classList.remove("carousel__button--selected")
	// 		);
	// 		items[i].classList.add("carousel__item--selected");
	// 		bottomButtons[i].classList.add("carousel__button--selected");
	// 		topButtons[i].classList.add("carousel__button--selected");
	// 	});
	