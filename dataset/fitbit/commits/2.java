public class Plugin extends Aware_Plugin {
    private class FibitDataSync extends AsyncTask<Void, Void, Void> {
        @Override
        protected Void doInBackground(Void... params) {
            try {
                if (Plugin.fitbitAPI == null) restoreFitbitAPI(getApplicationContext());

                String devices;
                try {
                    devices = fetchData(getApplicationContext(), "https://api.fitbit.com/1/user/-/devices.json");
                } catch (OAuthException e) {
                    if (DEBUG) Log.d(TAG, "Failed to connect to the server: api.fitbit.com. Problem with your internet connection.");
                    e.printStackTrace();
                    devices = null;
                }
                if (devices == null) return null;

                //Get data now that we have authenticated with Fitbit
                JSONArray devices_fitbit = new JSONArray(devices);
                if (DEBUG) Log.d(TAG, "Latest info on server (devices): " + devices_fitbit.toString(5));

                for (int i = 0; i < devices_fitbit.length(); i++) {

                    JSONObject fit = devices_fitbit.getJSONObject(i);

                    Cursor device = getContentResolver().query(Provider.Fitbit_Devices.CONTENT_URI, null, Provider.Fitbit_Devices.FITBIT_ID + " LIKE '" + fit.getString("id") + "'", null, Provider.Fitbit_Devices.TIMESTAMP + " DESC LIMIT 1");
                    if (device != null && device.moveToFirst()) {

                        JodaTimeAndroid.init(getApplicationContext());
                        DateTime localSync = DateTime.parse(device.getString(device.getColumnIndex(Provider.Fitbit_Devices.LAST_SYNC)));
                        DateTime serverSync = DateTime.parse(fit.getString("lastSyncTime"));

                        Cursor localData = getContentResolver().query(Provider.Fitbit_Data.CONTENT_URI, null, null, null, null);
                        if (!localSync.isEqual(serverSync) || (localData == null || localData.getCount() == 0)) {

                            String localSyncDate = device.getString(device.getColumnIndex(Provider.Fitbit_Devices.LAST_SYNC)).split("T")[0];
                            String serverSyncDate = fit.getString("lastSyncTime").split("T")[0];

                            String steps = fetchData(getApplicationContext(), "https://api.fitbit.com/1/user/-/activities/steps/date/" + localSyncDate + "/" + serverSyncDate + "/" + Aware.getSetting(getApplicationContext(), Settings.FITBIT_GRANULARITY) + ".json");
                            if (steps == null) {
                                if (DEBUG)
                                    Log.d(TAG, "No steps for this device.");
                            } else {
                                JSONObject steps_data = new JSONObject(steps);
                                ContentValues stepsData = new ContentValues();
                                stepsData.put(Provider.Fitbit_Data.TIMESTAMP, System.currentTimeMillis());
                                stepsData.put(Provider.Fitbit_Data.DEVICE_ID, Aware.getSetting(getApplicationContext(), Aware_Preferences.DEVICE_ID));
                                stepsData.put(Provider.Fitbit_Data.FITBIT_ID, fit.getString("id"));
                                stepsData.put(Provider.Fitbit_Data.DATA_TYPE, "steps");
                                stepsData.put(Provider.Fitbit_Data.FITBIT_JSON, steps_data.toString());
                                getContentResolver().insert(Provider.Fitbit_Data.CONTENT_URI, stepsData);

                                if (DEBUG)
                                    Log.d(TAG, "New steps: " + steps_data.toString(5));
                            }

                            String calories = fetchData(getApplicationContext(), "https://api.fitbit.com/1/user/-/activities/calories/date/" + localSyncDate + "/" + serverSyncDate + "/" + Aware.getSetting(getApplicationContext(), Settings.FITBIT_GRANULARITY) + ".json");
                            if (calories == null) {
                                if (DEBUG)
                                    Log.d(TAG, "No steps for this device.");
                            } else {
                                JSONObject calories_data = new JSONObject(calories);
                                ContentValues caloriesData = new ContentValues();
                                caloriesData.put(Provider.Fitbit_Data.TIMESTAMP, System.currentTimeMillis());
                                caloriesData.put(Provider.Fitbit_Data.DEVICE_ID, Aware.getSetting(getApplicationContext(), Aware_Preferences.DEVICE_ID));
                                caloriesData.put(Provider.Fitbit_Data.FITBIT_ID, fit.getString("id"));
                                caloriesData.put(Provider.Fitbit_Data.DATA_TYPE, "calories");
                                caloriesData.put(Provider.Fitbit_Data.FITBIT_JSON, calories_data.toString());
                                getContentResolver().insert(Provider.Fitbit_Data.CONTENT_URI, caloriesData);

                                if (DEBUG)
                                    Log.d(TAG, "New calories: " + calories_data.toString(5));
                            }

                            String heartrate;
                            if (Aware.getSetting(getApplicationContext(), Settings.FITBIT_HR_GRANULARITY).equalsIgnoreCase("1min")) {
                                heartrate = fetchData(getApplicationContext(), "https://api.fitbit.com/1/user/-/activities/heart/date/" + localSyncDate + "/" + serverSyncDate + "/" + Aware.getSetting(getApplicationContext(), Settings.FITBIT_HR_GRANULARITY) + ".json");
                            } else {
                                heartrate = fetchData(getApplicationContext(), "https://api.fitbit.com/1/user/-/activities/heart/date/" + serverSyncDate + "/1d/" + Aware.getSetting(getApplicationContext(), Settings.FITBIT_HR_GRANULARITY) + ".json");
                            }

                            if (heartrate == null) {
                                if (DEBUG)
                                    Log.d(TAG, "No heartrate for this device.");
                            } else {
                                JSONObject heartrate_data = new JSONObject(heartrate);
                                ContentValues heartRateData = new ContentValues();
                                heartRateData.put(Provider.Fitbit_Data.TIMESTAMP, System.currentTimeMillis());
                                heartRateData.put(Provider.Fitbit_Data.DEVICE_ID, Aware.getSetting(getApplicationContext(), Aware_Preferences.DEVICE_ID));
                                heartRateData.put(Provider.Fitbit_Data.FITBIT_ID, fit.getString("id"));
                                heartRateData.put(Provider.Fitbit_Data.DATA_TYPE, "heartrate");
                                heartRateData.put(Provider.Fitbit_Data.FITBIT_JSON, heartrate_data.toString());
                                getContentResolver().insert(Provider.Fitbit_Data.CONTENT_URI, heartRateData);

                                if (DEBUG) Log.d(TAG, "New heartrate: " + heartrate_data.toString(5));
                            }

                            //will have all the sleep related data from yesterday until today
                            JSONArray sleep = new JSONArray();
                            localSync = localSync.minusDays(1);
                            String sleep_efficiency = fetchData(getApplicationContext(), "https://api.fitbit.com/1/user/-/sleep/efficiency/date/" + localSync.toString(DateTimeFormat.forPattern("yyyy-MM-dd")) + "/" + serverSyncDate + ".json");
                            if (sleep_efficiency == null) {
                                if (DEBUG)
                                    Log.d(TAG, "No sleep efficiency for this device.");
                            } else {
                                JSONObject efficiency_data = new JSONObject(sleep_efficiency);
                                sleep.put(efficiency_data);
                            }
                            String sleep_time_in_bed = fetchData(getApplicationContext(), "https://api.fitbit.com/1/user/-/sleep/timeInBed/date/" + localSync.toString(DateTimeFormat.forPattern("yyyy-MM-dd")) + "/" + serverSyncDate + ".json");
                            if (sleep_time_in_bed == null) {
                                if (DEBUG)
                                    Log.d(TAG, "No sleep time to bed for this device.");
                            } else {
                                JSONObject time_to_bed_data = new JSONObject(sleep_time_in_bed);
                                sleep.put(time_to_bed_data);
                            }
                            String sleep_minutes_awake = fetchData(getApplicationContext(), "https://api.fitbit.com/1/user/-/sleep/minutesAwake/date/" + localSync.toString(DateTimeFormat.forPattern("yyyy-MM-dd")) + "/" + serverSyncDate + ".json");
                            if (sleep_minutes_awake == null) {
                                if (DEBUG)
                                    Log.d(TAG, "No sleep minutes awake for this device.");
                            } else {
                                JSONObject minutes_awake_data = new JSONObject(sleep_minutes_awake);
                                sleep.put(minutes_awake_data);
                            }
                            String sleep_minutes_to_sleep = fetchData(getApplicationContext(), "https://api.fitbit.com/1/user/-/sleep/minutesToFallAsleep/date/" + localSync.toString(DateTimeFormat.forPattern("yyyy-MM-dd")) + "/" + serverSyncDate + ".json");
                            if (sleep_minutes_to_sleep == null) {
                                if (DEBUG)
                                    Log.d(TAG, "No sleep minutes to sleep for this device.");
                            } else {
                                JSONObject minutes_to_sleep_data = new JSONObject(sleep_minutes_to_sleep);
                                sleep.put(minutes_to_sleep_data);
                            }
                            String sleep_awake_count = fetchData(getApplicationContext(), "https://api.fitbit.com/1/user/-/sleep/awakeningsCount/date/" + localSync.toString(DateTimeFormat.forPattern("yyyy-MM-dd")) + "/" + serverSyncDate + ".json");
                            if (sleep_awake_count == null) {
                                if (DEBUG)
                                    Log.d(TAG, "No sleep awake count for this device.");
                            } else {
                                JSONObject awake_count_data = new JSONObject(sleep_awake_count);
                                sleep.put(awake_count_data);
                            }
                            String sleep_details = fetchData(getApplicationContext(), "https://api.fitbit.com/1/user/-/sleep/list/date/" + localSync.toString(DateTimeFormat.forPattern("yyyy-MM-dd")) + "/" + serverSyncDate + ".json");
                            if (sleep_details == null) {
                                if (DEBUG)
                                    Log.d(TAG, "No sleep detailed list for this device.");
                            } else {
                                JSONObject sleep_details_data = new JSONObject(sleep_details);
                                sleep.put(sleep_details_data);
                            }

                            if (sleep.length() > 0) {
                                ContentValues sleepData = new ContentValues();
                                sleepData.put(Provider.Fitbit_Data.TIMESTAMP, System.currentTimeMillis());
                                sleepData.put(Provider.Fitbit_Data.DEVICE_ID, Aware.getSetting(getApplicationContext(), Aware_Preferences.DEVICE_ID));
                                sleepData.put(Provider.Fitbit_Data.FITBIT_ID, fit.getString("id"));
                                sleepData.put(Provider.Fitbit_Data.DATA_TYPE, "sleep");
                                sleepData.put(Provider.Fitbit_Data.FITBIT_JSON, sleep.toString());
                                getContentResolver().insert(Provider.Fitbit_Data.CONTENT_URI, sleepData);

                                if (DEBUG)
                                    Log.d(TAG, "New sleep: " + sleep.toString(5));
                            }

                            //Save the latest sync time. We want to check later how often the fitbits actually synched.
                            ContentValues latestData = new ContentValues();
                            latestData.put(Provider.Fitbit_Devices.TIMESTAMP, System.currentTimeMillis());
                            latestData.put(Provider.Fitbit_Devices.DEVICE_ID, Aware.getSetting(getApplicationContext(), Aware_Preferences.DEVICE_ID));
                            latestData.put(Provider.Fitbit_Devices.FITBIT_ID, fit.getString("id"));
                            latestData.put(Provider.Fitbit_Devices.FITBIT_BATTERY, fit.getString("battery"));
                            latestData.put(Provider.Fitbit_Devices.FITBIT_VERSION, fit.getString("deviceVersion"));
                            latestData.put(Provider.Fitbit_Devices.FITBIT_MAC, fit.optString("mac", ""));
                            latestData.put(Provider.Fitbit_Devices.LAST_SYNC, fit.getString("lastSyncTime"));
                            getContentResolver().insert(Provider.Fitbit_Devices.CONTENT_URI, latestData);

                            if (CONTEXT_PRODUCER != null) CONTEXT_PRODUCER.onContext();
                        }
                        if (localData != null && !localData.isClosed()) localData.close();
                    }
                    if (device != null && !device.isClosed()) device.close();
                }
            } catch (JSONException e) {
                e.printStackTrace();
            }
            return null;
        }
    }
}
