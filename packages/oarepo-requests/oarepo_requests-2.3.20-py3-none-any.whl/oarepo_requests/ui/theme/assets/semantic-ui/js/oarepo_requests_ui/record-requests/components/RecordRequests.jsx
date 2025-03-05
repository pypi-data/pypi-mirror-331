import React, { useCallback } from "react";
import PropTypes from "prop-types";
import { CreateRequestButtonGroup, RequestListContainer } from ".";
import {
  RequestContextProvider,
  CallbackContextProvider,
} from "@js/oarepo_requests_common";
import {
  useQuery,
  useQueryClient,
  QueryClient,
  QueryClientProvider,
} from "@tanstack/react-query";
import { httpVnd } from "@js/oarepo_ui";
import { OverridableContext, overrideStore } from "react-overridable";
const overriddenComponents = overrideStore.getAll();

export const requestButtonsDefaultIconConfig = {
  delete_published_record: { icon: "trash" },
  publish_draft: { icon: "upload" },
  publish_new_version: { icon: "upload" },
  new_version: { icon: "tag" },
  edit_published_record: { icon: "pencil" },
  assign_doi: { icon: "address card" },
  delete_doi: { icon: "remove" },
  created: { icon: "paper plane" },
  initiate_community_migration: { icon: "exchange" },
  confirm_community_migration: { icon: "exchange" },
  secondary_community_submission: { icon: "users" },
  remove_secondary_community: { icon: "remove" },
  submitted: { icon: "clock" },
  default: { icon: "plus" },
};

const queryClient = new QueryClient();

const RecordRequests = ({
  record: initialRecord,
  ContainerComponent,
  onBeforeAction,
  onAfterAction,
  onActionError,
  requestButtonsIconsConfig,
}) => {
  const queryClient = useQueryClient();

  const {
    data: requestTypes,
    error: applicableRequestsLoadingError,
    isFetching: applicableRequestTypesLoading,
  } = useQuery(
    ["applicableRequestTypes"],
    () => httpVnd.get(initialRecord.links["applicable-requests"]),
    {
      enabled: !!initialRecord.links?.["applicable-requests"],
      refetchOnWindowFocus: false,
    }
  );
  const {
    data: recordRequests,
    error: requestsLoadingError,
    isFetching: requestsLoading,
  } = useQuery(["requests"], () => httpVnd.get(initialRecord.links?.requests), {
    enabled: !!initialRecord.links?.requests,
    refetchOnWindowFocus: false,
  });
  const applicableRequestTypes = requestTypes?.data?.hits?.hits;

  const requests = recordRequests?.data?.hits?.hits;
  const fetchNewRequests = useCallback(() => {
    queryClient.invalidateQueries(["applicableRequestTypes"]);
    queryClient.invalidateQueries(["requests"]);
  }, [queryClient]);
  return (
    <RequestContextProvider
      value={{
        requests,
        requestTypes: applicableRequestTypes,
        record: initialRecord,
        requestButtonsIconsConfig: {
          ...requestButtonsDefaultIconConfig,
          ...requestButtonsIconsConfig,
        },
      }}
    >
      <CallbackContextProvider
        value={{
          onBeforeAction,
          onAfterAction,
          onActionError,
          fetchNewRequests,
        }}
      >
        <ContainerComponent>
          <CreateRequestButtonGroup
            applicableRequestsLoading={applicableRequestTypesLoading}
            applicableRequestsLoadingError={applicableRequestsLoadingError}
          />
          <RequestListContainer
            requestsLoading={requestsLoading}
            requestsLoadingError={requestsLoadingError}
          />
        </ContainerComponent>
      </CallbackContextProvider>
    </RequestContextProvider>
  );
};

RecordRequests.propTypes = {
  record: PropTypes.object.isRequired,
  ContainerComponent: PropTypes.func,
  onBeforeAction: PropTypes.func,
  onAfterAction: PropTypes.func,
  onActionError: PropTypes.func,
  requestButtonsIconsConfig: PropTypes.object,
};

const RecordRequestsWithQueryClient = ({
  record: initialRecord,
  ContainerComponent,
  onBeforeAction,
  onAfterAction,
  onActionError,
  requestButtonsIconsConfig,
}) => {
  return (
    <OverridableContext.Provider value={overriddenComponents}>
      <QueryClientProvider client={queryClient}>
        <RecordRequests
          record={initialRecord}
          ContainerComponent={ContainerComponent}
          onBeforeAction={onBeforeAction}
          onAfterAction={onAfterAction}
          onActionError={onActionError}
          requestButtonsIconsConfig={requestButtonsIconsConfig}
        />
      </QueryClientProvider>
    </OverridableContext.Provider>
  );
};

RecordRequestsWithQueryClient.propTypes = {
  record: PropTypes.object.isRequired,
  ContainerComponent: PropTypes.func,
  onBeforeAction: PropTypes.func,
  onAfterAction: PropTypes.func,
  onActionError: PropTypes.func,
  requestButtonsIconsConfig: PropTypes.object,
};

const ContainerComponent = ({ children }) => (
  <div className="requests-container borderless">{children}</div>
);

ContainerComponent.propTypes = {
  children: PropTypes.node,
};

RecordRequestsWithQueryClient.defaultProps = {
  ContainerComponent: ContainerComponent,
  onBeforeAction: undefined,
  onAfterAction: undefined,
  onActionError: undefined,
};

export { RecordRequestsWithQueryClient as RecordRequests };
