
Vacancy = Backbone.Model.extend()

var model = new Vacancy()
model.set({
    "name": "Hello world",
    "price": 100
});

var View = Backbone.View.extend({
    el: "#app",
    render: function(){
        var data = this.model.get("data");
        $el.append(data);
    }
});

view = View({model: model})
