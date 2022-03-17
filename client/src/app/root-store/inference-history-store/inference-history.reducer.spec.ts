import { keys } from 'lodash';
import { Action } from '@ngrx/store';

import { ProjectStatusNames } from '@store/project-store/project.model';
import { THROUGHPUT_UNIT } from '@store/model-store/model.model';

import { CompoundInferenceConfig } from '@shared/models/compound-inference-config';
import { DeviceTargets } from '@shared/models/device';

import { reducer } from './inference-history.reducer';
import { initialState } from './inference-history.state';
import { InferenceHistoryStoreActions, InferenceHistoryStoreReducer } from './';
import { IInferenceResult } from './inference-history.model';

const mockInferenceItemList: IInferenceResult[] = [
  {
    id: 3,
    profilingJobId: 1,
    projectId: 1,
    status: {
      errorMessage: 'Failed with an error',
      name: ProjectStatusNames.READY,
      progress: 100,
    },
    deviceType: DeviceTargets.CPU,
    created: Date.now(),
    updated: Date.now(),
    started: Date.now(),
    batch: 1,
    latency: 22.6903,
    nireq: 2,
    isAutoBenchmark: false,
    throughput: 80.6974,
    throughputUnit: THROUGHPUT_UNIT.FPS,
    autogenerated: false,
    totalExecutionTime: 20025.4,
    inferenceTime: 20,
  },
];

describe('InferenceHistory Reducer', () => {
  describe('an unknown action', () => {
    it('should return the previous state', () => {
      const action = {} as Action;

      const result = reducer(initialState, action);

      expect(result).toBe(initialState);
    });
  });

  describe('LOAD_INFERENCE_HISTORY action', () => {
    it('should set loading to true', () => {
      const action = InferenceHistoryStoreActions.loadInferenceHistory({ id: 1 });

      const state = InferenceHistoryStoreReducer(initialState, action);

      expect(state.isLoading).toEqual(true);
      expect(state.entities).toEqual(initialState.entities);
      expect(state.error).toBeNull();
    });
  });

  describe('LOAD_INFERENCE_HISTORY_FAILURE action', () => {
    it('should set error', () => {
      const error = { message: 'Error' };
      const action = InferenceHistoryStoreActions.loadInferenceHistoryFailure({ error });

      const loadAction = InferenceHistoryStoreActions.loadInferenceHistory({ id: 1 });
      const previousState = InferenceHistoryStoreReducer(initialState, loadAction);
      const state = InferenceHistoryStoreReducer(previousState, action);

      expect(state.error).toEqual(error);
      expect(state.isLoading).toEqual(false);
      expect(state.entities).toEqual(previousState.entities);
    });
  });

  describe('LOAD_INFERENCE_HISTORY_SUCCESS action', () => {
    it('should set all items', () => {
      const items = mockInferenceItemList as IInferenceResult[];
      const action = InferenceHistoryStoreActions.loadInferenceHistorySuccess({ items });

      const loadAction = InferenceHistoryStoreActions.loadInferenceHistory({ id: 1 });
      const previousState = InferenceHistoryStoreReducer(initialState, loadAction);
      const state = InferenceHistoryStoreReducer(previousState, action);

      expect(keys(state.entities).length).toEqual(mockInferenceItemList.length);
      expect(state.ids.length).toEqual(mockInferenceItemList.length);

      expect(state.error).toBeFalsy();
      expect(state.isLoading).toEqual(false);
    });
  });

  describe('ADD_RUN_INFERENCE_REQUEST action', () => {
    it('should set loading to true', () => {
      const action = InferenceHistoryStoreActions.addRunInferenceRequest({
        config: new CompoundInferenceConfig(),
      });

      const state = InferenceHistoryStoreReducer(initialState, action);

      expect(state.isLoading).toEqual(true);
      expect(state.entities).toEqual(initialState.entities);
      expect(state.error).toBeNull();
    });
  });

  describe('ADD_RUN_INFERENCE_FAILURE action', () => {
    it('should set error', () => {
      const error = { message: 'Error' };
      const action = InferenceHistoryStoreActions.addRunInferenceFailure({ error });

      const loadAction = InferenceHistoryStoreActions.addRunInferenceRequest({
        config: new CompoundInferenceConfig(),
      });
      const previousState = InferenceHistoryStoreReducer(initialState, loadAction);
      const state = InferenceHistoryStoreReducer(previousState, action);

      expect(state.error).toEqual(error);
      expect(state.isLoading).toEqual(false);
      expect(state.entities).toEqual(previousState.entities);
    });
  });

  describe('ADD_RUN_INFERENCE_SUCCESS action', () => {
    it('should set loading to false and remove error', () => {
      const action = InferenceHistoryStoreActions.addRunInferenceSuccess({
        projectId: 1,
        originalModelId: 1,
      });

      const loadAction = InferenceHistoryStoreActions.addRunInferenceRequest({
        config: new CompoundInferenceConfig(),
      });
      const previousState = InferenceHistoryStoreReducer(initialState, loadAction);
      const state = InferenceHistoryStoreReducer(previousState, action);

      expect(state.isLoading).toEqual(false);
      expect(state.error).toBeNull();
      expect(state.entities).toEqual(previousState.entities);
    });
  });

  describe('SET_RUNNING_INFERENCE_OVERLAY_ID action', () => {
    it('should set running inference overlay id', () => {
      const action = InferenceHistoryStoreActions.setRunningInferenceOverlayId({ id: '1' });

      const state = InferenceHistoryStoreReducer(initialState, action);

      expect(state.runningInferenceOverlayId).toEqual('1');
    });
  });
});
