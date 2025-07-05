// SleepLogList returns the sleep log list for based on given parameters
func (m *Session) SleepLogList(params LogListParameters) (SleepLogList, error) {
	parameterList := url.Values{}
	if params.BeforeDate != "" {
		parameterList.Add("beforeDate", params.BeforeDate)
		parameterList.Add("sort", "desc")
	} else if params.AfterDate != "" {
		parameterList.Add("afterDate", params.AfterDate)
		parameterList.Add("sort", "asc")
	} else {
		return SleepLogList{}, errors.New("beforeDate or afterDate must be given")
	}

	if params.Limit > 0 {
		if params.Limit > 20 {
			return SleepLogList{}, errors.New("limit must be 20 or less")
		}
		parameterList.Add("limit", strconv.Itoa(params.Limit))
	}

	parameterList.Add("offset", strconv.Itoa(params.Offset))

	contents, err := m.makeRequest("https://api.fitbit.com/1/user/-/sleep/list.json?" + parameterList.Encode())
	if err != nil {
		return SleepLogList{}, err
	}

	activityResponse := SleepLogList{}
	if err := json.Unmarshal(contents, &activityResponse); err != nil {
		return SleepLogList{}, err
	}

	return activityResponse, nil
}
