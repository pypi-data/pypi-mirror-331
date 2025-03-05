/*
Functions and routines associated with Enasis Network Common Library.

This file is part of Enasis Network software eco-system. Distribution
is permitted, for more information consult the project license file.
*/



/**
 * Assert the provided condition similar how using Python.
 *
 * @returns {Boolean} Boolean for the conditional outcome.
 */
function assert(
  condition,
) {

  if (condition)
    return true;

  throw new Error('Assertion'); }



/**
 * Attach the callback to the window session ready state.
 */
function whenready(
  callback,
) {

  assert(!isnull(callback));

  let state =
    document.readyState;

  if (state == 'loading')
    document
    .addEventListener(
      'DOMContentLoaded',
      callback);

  else callback(); }



/**
 * Return the boolean indicating the conditional outcome.
 *
 * @returns {Boolean} Boolean for the conditional outcome.
 */
function isnull(
  value,
) {

  let haystack = [null, undefined];

  if (haystack.includes(value))
    return true;

  return false; }



/**
 * Return the boolean indicating the conditional outcome.
 *
 * @returns {Boolean} Boolean for the conditional outcome.
 */
function isempty(
  value,
) {

  if (isstr(value))
    return value.length == 0;

  if (isdict(value)) {

    let keys =
      Object.keys(value)
      .length;

    if (length == 0)
        return true; }

  if (islist(value))
    return value.length == 0;

  return isnull(value); }



/**
 * Return the boolean indicating the conditional outcome.
 *
 * @returns {Boolean} Boolean for the conditional outcome.
 */
function isbool(
  value,
) {

  let haystack = [true, false];

  if (haystack.includes(value))
    return true;

  return false; }



/**
 * Return the boolean indicating the conditional outcome.
 *
 * @returns {Boolean} Boolean for the conditional outcome.
 */
function isstr(
  value,
) {

  if (typeof value === 'string')
    return true;

  return false; }



/**
 * Return the boolean indicating the conditional outcome.
 *
 * @returns {Boolean} Boolean for the conditional outcome.
 */
function isnum(
  value,
) {

  if (typeof value === 'number')
    return true;

  return false; }



/**
 * Return the boolean indicating the conditional outcome.
 *
 * @returns {Boolean} Boolean for the conditional outcome.
 */
function isquery(
  value,
) {

  try {

    if (value.enquery)
      return true; }

  catch (e) { }

  return false; }



/**
 * Return the boolean indicating the conditional outcome.
 *
 * @returns {Boolean} Boolean for the conditional outcome.
 */
function isnode(
  value,
) {

  if (value instanceof Node)
    return true;

  return false; }



/**
 * Return the boolean indicating the conditional outcome.
 *
 * @returns {Boolean} Boolean for the conditional outcome.
 */
function isnodes(
  value,
) {

  if (value instanceof NodeList)
    return true;

  return false; }



/**
 * Return the boolean indicating the conditional outcome.
 *
 * @returns {Boolean} Boolean for the conditional outcome.
 */
function istime(
  value,
) {

  let date =
    new Date(value);

  if (!isNaN(date.getTime()))
      return true;

  return false; }



/**
 * Return the boolean indicating the conditional outcome.
 *
 * @returns {Boolean} Boolean for the conditional outcome.
 */
function islist(
  value,
) {

  if (Array.isArray(value))
    return true;

  return false; }



/**
 * Return the boolean indicating the conditional outcome.
 *
 * @returns {Boolean} Boolean for the conditional outcome.
 */
function isdict(
  value,
) {

  if (typeof(value) == 'object'
      && !isnull(value)
      && !Array.isArray(value))
    return true;

  return false; }



/**
 * Return the boolean indicating the conditional outcome.
 *
 * @returns {Boolean} Boolean for the conditional outcome.
 */
function istrue(
  value,
) {

  if (value === true)
    return true;

  return false; }



/**
 * Return the boolean indicating the conditional outcome.
 *
 * @returns {Boolean} Boolean for the conditional outcome.
 */
function isfalse(
  value,
) {

  if (value === false)
    return true;

  return false; }



/**
 * Return the object value from the provided JSON string.
 */
function loads(
  value,
) {

  assert(isstr(value));

  return JSON.parse(value); }



/**
 * Return the JSON string from the provided object value.
 */
function dumps(
  value,
  indent=null,
) {

  assert(!isnull(value));
  assert(!isstr(value));

  let returned =
    JSON.stringify(
      value, null, indent);

  return returned; }
