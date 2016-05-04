var app = angular.module('myApp', []);

app.filter('slice', function() {
  return function(arr, start, end) {
    return arr.slice(start, end);
  };
});
app.controller('MainController', ['$scope', function($scope) {


  $scope.increasePage = function(index) {
    $scope.currentPage += 1;
  };

  $scope.decreasePage = function(index) {
    $scope.currentPage -= 1;
  };
$scope.plusOne =   function(index) {
  $scope.products[index].likes += 1;
};

$scope.minusOne = function(index) {
  $scope.products[index].dislikes += 1;
};

$scope.products = [
  {
  name: 'Program or be Programmed',
    cover: 'img/program-or-be-programmed.jpg' ,
    follow: 0
  },
  {
  name: 'Program or be Programmed',
    cover: 'img/program-or-be-programmed.jpg' ,
      follow: 0
  },
  {
  name: 'Program or be Programmed',
    cover: 'img/program-or-be-programmed.jpg' ,
    follow: 0
  },
  {
  name: 'Program or be Programmed',
  cover: 'img/program-or-be-programmed.jpg' ,
    follow: 0
  },
  {
  name: 'Program or be Programmed',
  cover: 'img/program-or-be-programmed.jpg' ,
    follow: 0

  }

]

  }]);
