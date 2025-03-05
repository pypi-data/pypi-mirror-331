/*
Functions and routines associated with Enasis Network Common Library.

This file is part of Enasis Network software eco-system. Distribution
is permitted, for more information consult the project license file.
*/



/**
 * Construct for containing the value status information.
 *
 * @returns {Object} jQuery-like object for the element.
 */
function statate(
  status,
  label=null,
  small=null,
) {

  assert(!isnull(status));


  let element =
    moderate(
      label,
      svgicon(status),
      small);


  element.addClass(
    'encommon_statate');

  element.attr(
    'data-status',
    status);


  return element; }
