##Modified for Practice -- Yash

include: "*.view" ## using include parameter we can include other project files here

##Below is actual code for view source referring to the database table.

#view: products {
#  sql_table_name: public.products ;;

## We can also extend another view and build on that

  #view: name_of_the_new_view {
  #  extends: [looker_events]

##Suppose we have our own query for the table we can use that directly here (can create one from SQL runner as well)
##The below query could contain data from multiple tables as well, Looker will add this query to the with statement as a whole

view: products {
  derived_table: {
    sql:
      SELECT * FROM  public.products ;;
  }

##Derived table parameters accepts a range of other parameters expecially related to persistent tables -- DB specific

## DISPLAY PARAMETERS - View level
  label: "Products_yash"
  ## just a label for display view, actual reference is by view name products

  ## FILTER PARAMETERS
  suggestions: yes

  dimension: id {
    primary_key: yes
    type: number
    sql: ${TABLE}.id ;;
    can_filter: no   # Restrict filtering on this
  }

 ## extension: required
##means this view cannot be used directly, needs to be extended and build upon, this will create a new copy of this view for every extension
##Refinment is required if same view is to be modified without making any changes to original file

#view: +view_name {
#  final: yes
#}

  dimension: cost {
    type: number
    sql: ${TABLE}.cost ;;
    value_format: "$0.00"
  }

  dimension: retail_price {
    type: number
    sql: ${TABLE}.retail_price ;;
    value_format_name: usd
  }
#add description
  dimension: sku {
    type: string
    description: "This is an sku field"
    sql: ${TABLE}.sku ;;
  }
  #hide a field from UI but can be used here
  dimension: sku2 {
    type: string
    hidden: yes
    sql: ${TABLE}.sku ;;
  }

  dimension: department {

    type: string



                        sql: ${TABLE}.department ;;

    suggestable: no
  }

  dimension: brand {
    type: string
    sql: ${TABLE}.brand ;;
    group_label: "Category & brand"
    link: {
      label: "Google Search"
      url: "http://www.google.com/search?q={{ value }}+Clothing"
      icon_url: "http://google.com/favicon.ico"

    }
  }
#Data based action , send emails, configure receiving server to do anything -- Action Hub -- sends Json on post
  dimension: name {
    type: string
    sql: ${TABLE}.name ;;
    action: {
      label: "Label to Appear in Action Menu"
    url: "https://google.com/search?q={{value}}"
    icon_url: "https://looker.com/favicon.ico"
    form_url:"https://google.com/search?q={{value}}"}
  }
#add group label to group together columns
  dimension: category {
    type: string
    sql: ${TABLE}.category ;;
    group_label: "Category & brand"
    drill_fields: [product_cat_details*]
    link: {
      label: "Go to look for  this category"
      url:"/looks/882?&f[products.category]={{ value }}"}
  }
  #Basic set
  set: product_cat_details {
    fields: [
      sku,
      brand,
      category
    ]
  }
  # Sets are mostly used as drill fields - Flexible in terms of what parameters it accepts
  set: product_multi_set {
    fields: [
      name,                  #dimension from this view
      product_cat_details*,   # set from this view
      users.country,
      total_cost,            #measure from this view
      users.count            #measure from another view

    ]
  }
#Add filters to measures will force them to be calculated in these values -



  measure: total_cost {
    type: sum
    sql: ${cost} ;;
    value_format_name: usd
    drill_fields: [product_cat_details*]
    link: {
      label: "Explore Top 20 Results"
      url: "{{ link }}&sorts=products.total_cost+desc&limit=20"
    }
  #filters: [users.country: "UK,USA,FR"]
  }

  measure: count {
    type: count
    #label: " @{creator} Count"
    drill_fields: [
      product_multi_set*,
      - sku        #removed one field from set
    ]
  }
}



#Case statement and dimension_group examples

view: order_items {
  sql_table_name: public.order_items ;;

  dimension: id {
    primary_key: yes
    type: number
    sql: ${TABLE}.id ;;
  }

  dimension: order_id {
    type: number
    hidden: yes
    sql: ${TABLE}.order_id ;;
  }

  dimension: inventory_item_id {
    type: number
    hidden: yes
    sql: ${TABLE}.inventory_item_id ;;
  }

  dimension_group: created {
    type: time
    timeframes: [
      raw,
      time,
      date,
      week,
      month,
      quarter,
      year
    ]
    sql: ${TABLE}.created_at ;;
  }

  dimension_group: shipped {
    type: time
    timeframes: [
      raw,
      time,
      date,
      week,
      month,
      quarter,
      year
    ]
    sql: ${TABLE}.shipped_at ;;
  }

  dimension_group: delivered {
    type: time
    timeframes: [
      raw,
      time,
      date,
      week,
      month,
      quarter,
      year
    ]
    sql: ${TABLE}.delivered_at ;;
  }

  dimension_group: returned {
    type: time
    timeframes: [
      raw,
      time,
      date,
      week,
      month,
      quarter,
      year
    ]
    sql: ${TABLE}.returned_at ;;
  }

  dimension: sale_price {
    type: number
    sql: ${TABLE}.sale_price ;;
    value_format_name: usd
  }

  dimension: price_range {
    case: {
      when: {
        sql: ${sale_price} < 20 ;;
        label: "Inexpensive"
      }
      when: {
        sql: ${sale_price} >= 20 AND ${sale_price} < 100 ;;
        label: "Normal"
      }
      when: {
        sql: ${sale_price} >= 100 ;;
        label: "Expensive"
      }
      else: "Unknown"
    }
  }

  dimension: status {
    type: string
    sql: ${TABLE}.status ;;
  }

  measure: count_complete {
    type: count
    filters: [status: "Complete"]
  }


  measure: per_complete {
    type: number
    sql: 100*${count_complete}/${count} ;;
    html: <p STYLE = "font-size : 5px">{{rendered_value}}</p> ;;
  }
  measure: count {
    type: count
    #html: <h1><font size="65">{{ value }}</font></h1>;;
    drill_fields: [
      id,
      created_time,
      shipped_time,
      delivered_time,
      returned_time,
      sale_price,
      status,
      products.name
    ]
  }

  measure: total_sale_price {
    type: sum
    sql: ${sale_price} ;;
  }

  measure: average_sale_price {
    type: average
    sql: ${sale_price} ;;
    #html: <font size="60">{{ value }}</font>;;
  }

  measure: total_profit {
    type: number
    sql: ${total_sale_price} - ${products.total_cost} ;;
   # html: <font size="90">{{ rendered_value }}</font>;;
    value_format_name: usd_0
  }

  measure: least_expensive_item {
    type: min
    sql: ${sale_price} ;;
  }

  measure: most_expensive_item {
    type: max
    sql: ${sale_price} ;;
  }
}



#map layer / tier/ location / order by field / liquid template language

view: users {
  sql_table_name: public.users ;;

  dimension: id {
    primary_key: yes
    type: number
    sql: ${TABLE}.id ;;
  }

  dimension_group: created {
    type: time
    timeframes: [
      raw,
      time,
      date,
      week,
      month,
      quarter,
      year
    ]
    sql: ${TABLE}.created_at ;;
  }

  dimension: first_name {
    type: string
    sql: ${TABLE}.first_name ;;
  }

  dimension: last_name {
    type: string
    sql: ${TABLE}.last_name ;;
  }

  dimension: full_name {
    type: string
    sql: ${first_name} || ' ' || ${last_name} ;;
    order_by_field: last_name
  }

  dimension: city {
    type: string
    sql: ${TABLE}.city ;;
  }

  dimension: state {
    type: string
    sql: ${TABLE}.state ;;
  }

  dimension: zip {
    type: zipcode
    sql: ${TABLE}.zip ;;
  }
#nneed to specify map layer name
  dimension: country {
    type: string
    sql: ${TABLE}.country ;;
    map_layer_name: countries
  }

  dimension: age {
    type: number
    sql: ${TABLE}.age ;;
  }

  dimension: age_tier {
    type: tier
    tiers: [0, 10, 20, 30, 40, 50, 60, 70, 80]
    style: integer
    sql: ${age} ;;
  }

  dimension: gender {
    type: string
    sql: ${TABLE}.gender ;;
  }

  dimension: email {
    type: string
    sql: ${TABLE}.email ;;
  }

  dimension: traffic_source {
    type: string
    sql: ${TABLE}.traffic_source ;;
  }

  dimension: latitude {
    type: number
    sql: ${TABLE}.latitude ;;
  }

  dimension: longitude {
    type: number
    sql: ${TABLE}.longitude ;;
  }

  dimension: location {
    type: location
    sql_latitude: ${latitude} ;;
    sql_longitude: ${longitude} ;;
  }

  dimension: distance_from_distribution_center {
    type: distance
    start_location_field: distribution_centers.location
    end_location_field: users.location
    units: miles
  }

  measure: count {
    type: count
    drill_fields: [id, first_name, last_name]
  }

  measure: men_count {
    type: count
    filters: {
      field: gender
      value: "Male"
    }
  link: {label: "Google Search"

     url:" {% if value > 1000 %} http://www.google.com/search?q={{ value }}+greater {% else %}http://www.google.com/search?q={{ value }}+less {% endif %}"
  }



  }

  measure: female_count {
    type: count
    filters: {
      field: gender
      value: "Female"
    }
  }
}
