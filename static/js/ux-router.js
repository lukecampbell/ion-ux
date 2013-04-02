// Temp: this will be delivered via the template preprocessor.
AVAILABLE_LAYOUTS = {
  'face': '2163152',
  'status': '2163153',
  'related': '2163154',
  'dashboard': '2163156',
  'command': '2163157'
};

LOADING_TEMPLATE = '<div style="text-align: center; padding-top: 100px;"><img src="/static/img/busy_indicator.gif"</div>'

IONUX.Router = Backbone.Router.extend({
  routes: {
    "": "dashboard",
    "search/?:query": "search",
    ":resource_type/list/": "collection",
    ":resource_type/command/:resource_id/": "command",
    ":resource_type/:view_type/:resource_id/" : "page",
    ":resource_type/:view_type/:resource_id/edit" : "edit",
    "userprofile" : "user_profile",
    "create_account": "create_account",
    'dev/dashboard': 'dev_dashboard',
    'dev/dashboard/map/:resource_id': 'map_resource'
  },


  dev_dashboard: function() {
    $('#footer').remove(); // Remove legacy footer.
    $('.wrapper').html($('#dashboard-tmpl').html());
    $('#main').html($('#dashboard-content-tmpl').html());

    new IONUX.Views.ViewControls().render().el;
    
    // Render Sidebar
    IONUX.Dashboard.SelectorResources = new IONUX.Collections.Observatories();
    IONUX.Dashboard.SelectorView = new IONUX.Views.ObservatorySelector({collection: IONUX.Dashboard.SelectorResources, title: 'Sites'});
    IONUX.Dashboard.SelectorResources.fetch({
      reset: true,
      success: function(resp){
        IONUX.Dashboard.Resources = new IONUX.Collections.DashboardResources(resp.models, {resource_id: null});
        IONUX.Dashboard.ActiveResource = new IONUX.Models.ActiveResource();
        new IONUX.Views.AssetMap({
          collection: IONUX.Dashboard.Resources,
          model: IONUX.Dashboard.ActiveResource
        });
        IONUX.Dashboard.Resources.trigger('update_markers');
        new IONUX.Views.MapFilter().render().el;
      },
    });
  },
  
  map_resource: function(resource_id){
    console.log('router map_resource', resource_id);
    $('#2163993').empty().append('<div style="margin-top:50px;" id="spinner"></div>');
    
    // Todo: move into it's own view for reuse;
    var opts = {
      lines: 13, // The number of lines to draw
      length: 7, // The length of each line
      width: 4, // The line thickness
      radius: 10, // The radius of the inner circle
      corners: 1, // Corner roundness (0..1)
      rotate: 0, // The rotation offset
      color: '#fff', // #rgb or #rrggbb
      speed: 1, // Rounds per second
      trail: 60, // Afterglow percentage
      shadow: false, // Whether to render a shadow
      hwaccel: false, // Whether to use hardware acceleration
      className: 'spinner', // The CSS class to assign to the spinner
      zIndex: 2e9, // The z-index (defaults to 2000000000)
      top: 'auto', // Top position relative to parent in px
      left: 'auto' // Left position relative to parent in px
    };
    var target = document.getElementById('spinner');
    var spinner = new Spinner(opts).spin(target);
        
    var active_resource_attributes = IONUX.Dashboard.SelectorResources.findWhere({_id: resource_id})['attributes'];
    // IONUX.Dashboard.ActiveResource.set(active_resource_attributes);
    IONUX.Dashboard.Resources.resource_id = resource_id;
    IONUX.Dashboard.Resources.set([]);
    IONUX.Dashboard.Resources.fetch({
      reset: true,
      success: function(resp) {
        IONUX.Dashboard.ActiveResource.set(active_resource_attributes);
        // console.log('ActiveResource', IONUX.Dashboard.ActiveResource.toJSON());
        // console.log('Resources', IONUX.Dashboard.Resources.toJSON());
      }
    });
  },

  edit: function(){
    var editable_resource = new IONUX.Models.EditableResource(window.MODEL_DATA.resource);
    new IONUX.Views.EditResource({model: editable_resource}).render().el;
  },
  search: function(query){
    $('#error').hide();
    $('#dynamic-container').show().html(LOADING_TEMPLATE);
    var search_model = new IONUX.Models.Search({search_query: query});
    search_model.fetch()
      .success(function(resp){
        console.log('Search success:', resp);
        $('#dynamic-container').html($('#2163152').html());
        $('.span9 li,.span3 li').hide();
        $('.v01 ul:visible, .v02 ul:visible').find('li:first').find('a').click();
        $('li.Collection ,div.Collection').show();
        $('.span9').find('li.Collection:first').find('a').click();
        var table_elmt = $('.v02 .Collection .table_ooi').first(); // Todo: better way of finding the container for the collection.
        var table_id = table_elmt.attr('id');
        new IONUX.Views.DataTable({el: $(table_elmt), data: resp.data});
        $('.heading').html('<h1>Search Results</h1>').css('padding-bottom', '15px'); // Temp: css hack to make layout nice.
      });
    new IONUX.Views.Footer({resource_id: null, resource_type: null}).render().el;
  },
  dashboard: function(){
    $('#dynamic-container').html($('#' + AVAILABLE_LAYOUTS['dashboard']).html()).show();
    $('.Collection').show();
    $('.heading, .v01').remove(); // Temp: element positioning
    $('.v02').removeClass('span9').addClass('span12');
    $('.v01 ul:visible, .v02 ul:visible').find('li:first').find('a').click();
    new IONUX.Views.DashboardMap({el: '.Collection .map_ooi'}).render().el;
    new IONUX.Views.Footer({resource_id: null, resource_type: null}).render().el;
    new IONUX.Views.Search({el: '#search'}).render().el;
  },
  collection: function(resource_type){
    $('#error').hide();
    $('#dynamic-container').show().html(LOADING_TEMPLATE);
    window.MODEL_DATA = new IONUX.Collections.Resources(null, {resource_type: resource_type});
    window.MODEL_DATA.fetch()
      .done(function(data){
        $('#dynamic-container').html($('#2163152').html());
        $('.span9 li,.span3 li').hide();
        $('.v01 ul:visible, .v02 ul:visible').find('li:first').find('a').click();
        $('li.Collection ,div.Collection').show();
        $('.span9').find('li.Collection:first').find('a').click();
        var table_elmt = $('.v02 .Collection .table_ooi').first(); // Todo: better way of finding the container for the collection.
        var table_id = table_elmt.attr('id');
        new IONUX.Views.DataTable({el: $(table_elmt), data: window.MODEL_DATA.toJSON()});
      });
    new IONUX.Views.Footer({resource_id: null, resource_type: resource_type}).render().el;
  },
  page: function(resource_type, view_type, resource_id){
    $('#error').hide();
    $('#dynamic-container').show().html(LOADING_TEMPLATE);
    var resource_extension = new IONUX.Models.ResourceExtension({resource_type: resource_type, resource_id: resource_id});
    resource_extension.fetch()
      .success(function(model, resp) {
        $('#dynamic-container').show();
        $('#dynamic-container').html($('#' + AVAILABLE_LAYOUTS[view_type]).html());
        $('.span9 li,.span3 li').hide();
        render_page(resource_type, resource_id, model);
      });
    new IONUX.Views.Footer({resource_id: resource_id, resource_type: resource_type}).render().el;
  },
  
  command: function(resource_type, resource_id){
    $('#error').hide();
    $('#dynamic-container').show();
    $('#dynamic-container').html($('#' + AVAILABLE_LAYOUTS['command']).html());
    $('.span9 li,.span3 li').hide();
    // $('.v02').empty();
    var resource_extension = new IONUX.Models.ResourceExtension({resource_type: resource_type, resource_id: resource_id});
    if (resource_type == 'InstrumentDevice') {
      new IONUX.Views.InstrumentCommandFacepage({model: resource_extension, el: '.v02'});
    } else if (resource_type == 'PlatformDevice') {
      new IONUX.Views.PlatformCommandFacepage({model: resource_extension, el: '.v02'});
    };
    resource_extension.fetch()
      .success(function(model, resp){
        render_page(resource_type, resource_id, model);
      });
    new IONUX.Views.Footer({resource_id: null, resource_type: null}).render().el;
  },

  user_profile: function() {
    this._reset();
    var model = new IONUX.Models.UserRegistrationModel();
    model.fetch()
      .done(function(data) {
        $("#dynamic-container").show();
        //$("#dynamic-container").html(data);
        new IONUX.Views.EditUserRegistration({model: model}).render();
      });
  },

  create_account: function() {
    new IONUX.Views.CreateAccountView().render();
  },

    // KEPT FOR REFERENCE
    // user_profile: function() {
    //     this._reset();
    //     var fpModel = new IONUX.Models.UserRegistrationModel();
    //     new IONUX.Views.UserRegistration({model:fpModel});
    //     fpModel.fetch();
    // },
  
    // KEPT FOR REFERENCE - ALEX'S USER REQUESTS
    // observatory_facepage: function(observatory_id){
    //     this._reset();
    //     var fpModel = new IONUX.Models.ObservatoryFacepageModel({observatory_id:observatory_id});
    //     new IONUX.Views.ObservatoryFacepage({model:fpModel});
    //     fpModel.fetch();
    // 
    //     var urCollection = new IONUX.Collections.UserRequestCollection();
    //     urCollection.observatory_id = observatory_id; //XXX better way to set this?
    //     var userRequestsView = new IONUX.Views.UserRequestsView({collection:urCollection, facepage_model: fpModel});
    //     urCollection.fetch();
    // },
        
  handle_navigation: function(){
    var self = this;
    $(document).on("click", "a", function(e) {
      var target = $(e.target);
      if (target.hasClass('external')) return true;
      // TEMP: catching links in Google Maps, also catching download links.
      var href = target.attr('href'); 
      if (!href) return true;
      if (href.match(/^http/)) return true;
      // Catch Bootstrap's tabs hash so URL doesn't change, example: "InstrumentDevice/list/" to "/2150593"
      if (target.attr('data-toggle') == 'tab') return true;
      self.navigate($(this).attr('href'), {trigger:true});
      return false;
    });
  },
    
  // // graceful Backbone handling of full page refresh on non '/' url.
  // handle_url: function(current_url){
  //     if (current_url != "/"){
  //         this.navigate(current_url, {trigger:true});
  //     }
  // },

  _reset: function(){ //reset the UI
    $(".viewcontainer").hide();
  }
});


// ----------------------------------------------------------------------------
// HELPER METHODS - TODO: move into IONUX namespace
// ----------------------------------------------------------------------------

// Look up chained values found in data-path
function get_descendant_properties(obj, desc) {
  var arr = desc.split(".");
  while(arr.length && (obj = obj[arr.shift()]));
  return obj;
};

// Create <a href> from text
function replace_url_with_html_links(text) {
  var exp = /(\b(https?|ftp|file):\/\/[-A-Z0-9+&@#\/%?=~_|!:,.;]*[-A-Z0-9+&@#\/%=~_|])/ig;
  return text.replace(exp,"<a class='external' target='_blank' href='$1'>$1</a>"); 
};

// Returns a displayable resource type for the resource_type given.
// If the type is not displayable, traverse up the heirarchy of resources
// until one is found.
function get_renderable_resource_type(resource_type)
{
  // FIX/HACK: Observatory shouldn't be on its own, it should be a site
  if (resource_type == "Observatory")
    return "Site";

  // conduct initial search of window.LAYOUT
  var re = _.find(window.LAYOUT.spec.restypes, function(v, k) { return v.name == resource_type; });

  while (re != null) {
    if ($("." + re.name).length > 0)
      return re.name;

    re = window.LAYOUT.spec.restypes[re.super];
  }

  // unknown?
  return "Resource";
}

// Renders a page based on resource_type
function render_page(resource_type, resource_id, model) {
  var start_render = new Date().getTime();

   // get most displayable resource type - by derived or otherwise
  resource_type = get_renderable_resource_type(resource_type);
  
  window.MODEL_DATA = model.data;
  window.MODEL_DATA['resource_type'] = resource_type;

  var attribute_group_elmts = $('.'+resource_type+' .attribute_group_ooi');
  _.each(attribute_group_elmts, function(el){
      var data_path = $(el).data('path');
      var data = get_descendant_properties(window.MODEL_DATA, data_path);
      new IONUX.Views.AttributeGroup({el: $(el), data: window.MODEL_DATA}).render().el;
  });

  var text_static_elmts = $('.'+resource_type+' .text_static_ooi');
  _.each(text_static_elmts, function(el){
      new IONUX.Views.TextStatic({el: $(el)}).render().el;
  });

  var text_short_elmts = $('.'+resource_type+' .text_short_ooi');
  _.each(text_short_elmts, function(el){
      new IONUX.Views.TextShort({el: $(el), data_model: window.MODEL_DATA}).render().el;
  });

  var text_extended_elmts = $('.'+resource_type+' .text_extended_ooi');
  _.each(text_extended_elmts, function(el){
      new IONUX.Views.TextExtended({el: $(el), data_model: window.MODEL_DATA}).render().el;
  });

  var icon_elmts = $('.'+resource_type+' .icon_ooi');
  _.each(icon_elmts, function(el) {
      new IONUX.Views.Icon({el: $(el)}).render().el;
  });

  _.each($('.'+resource_type+' .image_ooi'), function(el) {
      var data_path = $(el).data('path');
      var data = get_descendant_properties(window.MODEL_DATA, data_path);
      switch(data){
          case 1:
              $(el).html($('<span>').addClass('badge_status_graphic_ok').html('&nbsp;'));
              break;
          case 2:
              $(el).html($('<span>').addClass('badge_status_graphic_warning').html('&nbsp;'));
              break;
          case 3:
              $(el).html($('<span>').addClass('badge_status_graphic_critical').html('&nbsp;'));
              break;
          default:
              $(el).html($('<span>').addClass('badge_status_graphic_unknown').html('&nbsp;'));
      };
  });

  var badge_elmts = $('.'+resource_type+' .badge_ooi');
  _.each(badge_elmts, function(el) {
    new IONUX.Views.Badge({el: $(el), data_model: window.MODEL_DATA}).render().el;
  });
  
  var list_elmts = $('.'+resource_type+' .list_ooi');
  _.each(list_elmts, function(el) {
    new IONUX.Views.List({el: $(el), data_model: window.MODEL_DATA}).render().el;
  });
  
  var table_elmts = $('.'+resource_type+' .table_ooi');
  _.each(table_elmts, function(el) {
    var data_path = $(el).data('path');
    var raw_table_data = get_descendant_properties(window.MODEL_DATA, data_path);
    if (!_.isEmpty(raw_table_data)) {
        var table = new IONUX.Views.DataTable({el: $(el), data: raw_table_data});
    } else {
        var table = new IONUX.Views.DataTable({el: $(el), data: []});
    };
    
    // TODO: find a better way of putting a header in table that is not
    // the first/only item in a .tab-pane.
    var elements_len = $(el).closest('.tab-pane').find('.'+resource_type).length;
    if (elements_len > 1){
      var heading = $(el).data('label');
      $(el).find('.filter-header').prepend('<div class="table-heading">'+heading+'</div>');
    };
  
    $(el).find('table').last().dataTable().fnAdjustColumnSizing();
  });
  
  var extent_geospatial_elmts = $('.'+resource_type+' .extent_geospatial_ooi');
  _.each(extent_geospatial_elmts, function(el) {
    var data_path = $(el).data('path');
    var data = get_descendant_properties(window.MODEL_DATA, data_path);
    if (data) new IONUX.Views.ExtentGeospatial({el: $(el), data: data}).render().el;
  });
  
  var extent_vertical_elmts = $('.'+resource_type+' .extent_vertical_ooi');
  _.each(extent_vertical_elmts, function(el){
    var data_path = $(el).data('path');
    var data = get_descendant_properties(window.MODEL_DATA, data_path);
    if (data) new IONUX.Views.ExtentVertical({el: $(el), data: data}).render().el;
  });

  var extent_temporal_elmts = $('.'+resource_type+' .extent_temporal_ooi');
  _.each(extent_temporal_elmts, function(el) {
    new IONUX.Views.ExtentTemporal({el: $(el)}).render().el;
  });

  var checkbox_elmts = $('.'+resource_type+' .checkbox_ooi');
  _.each(checkbox_elmts, function(el) {
    new IONUX.Views.Checkbox({el: $(el), data_model: window.MODEL_DATA}).render().el;
  });
  
  if (resource_type == 'DataProduct') {
    var chart_elmt = $('.'+resource_type+' .chart_ooi').first();
    chart_elmt.css({height: '350px', width: '100%'});
    // new IONUX.Views.Chart({resource_id: resource_id, el: chart_elmt}).render().el;
    chart_elmt.html('<iframe width="100%" height="100%" id="chart" src="/static/visualization/chart.html"></iframe>')
    
    // Todo: manually setting the ERDAP download link
    var data_url_text = $('#2164346').text();
    $('#2164346').html(replace_url_with_html_links(data_url_text));
    
    // Todo: find the cause of double content-wrapping on these two items
    $('#2163118 .content-wrapper:last').remove();
    $('#2164400 .content-wrapper:last').remove();
  };
  
  _.each($('.v02 .'+resource_type), function(el){
    $(el).find('.content-wrapper:first').css('height', '200px').jScrollPane({autoReinitialise: true});
  });
  

  // Action Menus
  
  _.each($('.v01 .group .nav, .v02 .group .nav'), function(el) {
    // Todo: finish attachments/events menus
    var group_name = $(el).find('li:first a').text();
    switch(group_name){
      case 'Attachments':
        new IONUX.Views.AttachmentActions({el:$(el)});
        break;
      case 'Recent Events':
        new IONUX.Views.EventActions({el:$(el)});
        break;
      case 'Participants':
        new IONUX.Views.NegotiationActions({el: $(el)});
        break;
      default:
        new IONUX.Views.GroupActions({el:$(el)});
    };
  });
  
  _.each($('.v01 .'+resource_type+'.block, .v02 .'+resource_type+'.block'), function(el) {
    new IONUX.Views.BlockActions({el:$(el)});
  });
  
  new IONUX.Views.ViewActions({el: '.'+resource_type+' .heading-right'});

  // Show the relevant elements and click to enable the Bootstrap tabs.
  $('li.' + resource_type + ', div.' + resource_type).show();
  $('.span9 ul, .span3 ul, .span12 ul').find('li.' + resource_type + ':first').find('a').click();  
  $('.tab-pane').find('.'+resource_type+':visible:first').css('margin-left', 0);
  // DataTables column sizing
  $('a[data-toggle="tab"]').on('shown', function (e){
    var table = $($(e.target).attr('href')).find('.'+resource_type+' .table_ooi');
    if (table.length) $(table).find('table').last().dataTable().fnAdjustColumnSizing();
  });
  _.each($('.'+resource_type+' .table_ooi'), function(table){
    $(table).find('table').last().dataTable().fnAdjustColumnSizing();
  });
  
  console.log('render_page elapsed: ', new Date().getTime() - start_render);
};
